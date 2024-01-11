import json
import os
import re
import time
from urllib.parse import parse_qs, urlencode

import requests

import config


class StrangeError(Exception):
    code: int = None
    msg: str = None

    def __init__(self, code, msg):
        super().__init__()
        self.code = code
        self.msg = msg

    def __str__(self):
        return f'{self.code} | {self.msg}'


class NoRouteError(Exception):
    pass


class Strange:
    url: str = None
    app_id: str = None
    security: str = None
    crt: str = None
    env: str = None
    token: str = None
    sk_file: str = 'apollo/sk'

    def __init__(self, url: str, app_id: str, security: str, env: str, sk_file: str = 'apollo/sk'):
        self.url = url
        self.app_id = app_id
        self.security = security
        self.env = env
        self.sk_file = sk_file
        print(f'Strange: url={url}, app_id={app_id}, env={env}, sk_file={sk_file}')
        self.dump_sk()

    def dump_sk(self):
        if os.path.exists(self.sk_file):
            with open(self.sk_file, 'r', encoding='utf-8') as file:
                content = file.read()
                print(f'sk: {content}')

    def refresh_token(self):
        url = f'{self.url}/account/verify'
        r = requests.post(url, json={
            'name': self.app_id,
            'security': self.security
        }, verify=False)
        if r.status_code != 200:
            raise StrangeError(500, r.text)
        data = r.json()
        if data['code'] != 200:
            raise StrangeError(data['code'], data['msg'])
        token = data['data']

        # 更新token和过期时间
        self.token = token
        now_time = int(time.time())
        expire_at = now_time + 24 * 60 * 60
        self.__setattr__('token_expire_at', expire_at)

    def validate_token(self):
        now_time = int(time.time())
        if not hasattr(self, "token_expire_at"):
            self.refresh_token()
        else:
            # 判断当前时间是否大于token的有效时间
            if now_time > self.token_expire_at:
                # 如果token过期，将过期的token值删掉，重新调起token方法
                delattr(self, "token")
                self.refresh_token()

    def fetch_resource(self) -> dict:
        self.validate_token()

        url = f'{self.url}/resource/fetchAllByToken?env={self.env}'
        r = requests.get(url, headers={
            'token': self.token
        }, verify=False)
        if r.status_code != 200:
            raise StrangeError(500, r.text)
        data = r.json()
        print(f'StrangeResource: {json.dumps(data)}')
        if data['code'] != 200 and data['msg'] == '无权访问':
            self.refresh_token()
        res_map = data['data']
        return res_map


class StrangeAdapter:
    client: Strange = None

    @classmethod
    def update_env(cls, env, value):
        if value:
            os.environ[env] = value

    @classmethod
    def find_between_symbols(cls, text, symbol1, symbol2):
        pattern = re.escape(symbol1) + "(.*?)" + re.escape(symbol2)
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        else:
            return None

    def init(self):
        app_id = config.get_env('STRANGE_APP_ID')
        if not app_id:
            return

        env = config.get_env('RUNTIME_ENV')
        if not env:
            raise ValueError('Required env RUNTIME_ENV')
        strange_url = config.get_env('STRANGE_URL')
        if not strange_url:
            raise ValueError('Required env STRANGE_URL')
        strange_security = config.get_env('STRANGE_APP_SECURITY')
        if not strange_security:
            raise ValueError('Required env STRANGE_APP_SECURITY')
        sk_file = config.get_env('SK_FILE')
        if not sk_file:
            sk_file = '/home/docker/apollo/sk'

        self.client = Strange(strange_url.strip(), app_id.strip(), strange_security.strip(), env.strip(), sk_file)
        res_dict = self.client.fetch_resource()
        if res_dict:
            self.update_env_from_strange(res_dict)

    def update_env_from_strange(self, res_dict: dict):
        if config.get_env('REDIS_DB_ROUTE'):
            self.update_redis_config(res_dict[config.get_env('REDIS_DB_ROUTE')])
        if config.get_env('DB_DATABASE_ROUTE'):
            self.update_db_config(res_dict[config.get_env('DB_DATABASE_ROUTE')])

    def update_redis_config(self, routes):
        if not routes:
            raise NoRouteError()

        route = routes[0]
        c = json.loads(route['config'])
        address = str(route['address']).split(':')
        host = address[0]
        port = address[1]
        user = None
        password = route['password']
        db = c['db']
        self.update_env('REDIS_HOST', host)
        self.update_env('REDIS_PORT', port)
        self.update_env('REDIS_USERNAME', user)
        self.update_env('REDIS_PASSWORD', password)
        self.update_env('REDIS_DB', db)
        print(f'Strange(redis): host={host}, port={port}')

    def update_db_config(self, routes):
        if not routes:
            raise NoRouteError()

        route = routes[0]
        address = str(route['address']).split('?')
        extras = parse_qs(address[1])
        host = route['host']
        port = route['port']
        user = route['username']
        password = route['password']
        database = route['databaseName']
        self.update_env('DB_TYPE', 'mysql')
        self.update_env('DB_HOST', host)
        self.update_env('DB_PORT', str(port))
        self.update_env('DB_USERNAME', user)
        self.update_env('DB_PASSWORD', password)
        self.update_env('DB_DATABASE', database)
        extras_kwargs = {
            'charset': 'utf8',
            'use_unicode': True,
        }
        self.update_env('DB_EXTRAS', urlencode(extras_kwargs))
        print(f'Strange(db): host={host}, port={port}, db={database}')


def init():
    strange.init()


strange = StrangeAdapter()
