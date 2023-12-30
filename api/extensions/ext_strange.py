import time

import requests
from flask import Flask

from extensions.ext_apollo import ApolloData


class StrangeError(Exception):
    code: int = None
    msg: str = None

    def __init__(self, code, msg):
        super().__init__()
        self.code = code
        self.msg = msg


class Strange:
    url: str = None
    app: str = None
    security: str = None
    crt: str = None
    env: str = None
    token: str = None

    def __init__(self, url, app, security, crt, env):
        self.url = url
        self.app = app
        self.security = security
        self.crt = crt
        self.env = env

    def refresh_token(self):
        url = f'{self.url}/account/verify'
        r = requests.post(url, json={
            'name': self.app,
            'security': self.security
        })
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

    def fetch_resource(self) -> map:
        self.validate_token()

        url = f'{self.url}/resource/fetchAllByToken?env={self.env}'
        r = requests.get(url, headers={
            'token': self.token
        })
        if r.status_code != 200:
            raise StrangeError(500, r.text)
        data = r.json()
        if data['code'] != 200 and data['msg'] == '无权访问':
            self.refresh_token()
        res_map = data['data']
        return res_map


class StrangeAdapter:
    client: Strange = None

    def init(self, app: Flask):
        strange_app = ApolloData.get('APOLLO_APP_ID')
        if not strange_app:
            raise ValueError('No strange app config')
        env = ApolloData.get('runtime.env')
        if not env:
            raise ValueError('No runtime.env')
        strange_url = ApolloData.get('http.address')
        if not strange_url:
            raise ValueError('No http.address')
        strange_security = ApolloData.get('strange.app.security')
        if not strange_security:
            raise ValueError('No strange.app.security')
        strange_crt = ApolloData.get('strange.crt')
        if not strange_crt:
            raise ValueError('No strange.crt')

        self.client = Strange(strange_url, strange_app, strange_security, strange_crt, env)
        res_map = self.client.fetch_resource()
        if not res_map:
            return
        self.update_env_from_strange(res_map)

    def update_env_from_strange(self, res_map: map):
        for res in res_map.items():
            print(res)


def init_app(app: Flask):
    strange.init(app)


strange = StrangeAdapter()
