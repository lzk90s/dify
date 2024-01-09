# -*- coding: utf-8 -*-
import logging
import os.path
import random
import threading

import requests
import yaml

import config

logger = logging.getLogger(__name__)


class GlobalVar(dict):
    """Global Vars"""
    name = 'apollo_client'

    def set(self, name, value):
        setattr(self, name, value)

    def get(self, name, default_value=None):
        return getattr(self, name, default_value)


ApolloData = GlobalVar()


def init_config(apollo_data: dict):
    """初始化配置信息"""
    # logging.getLogger(__name__).debug(f'get apollo data: {apollo_data}')
    for k, v in apollo_data.items():
        ApolloData.set(k, v)


class ApolloClient(object):
    """Get config from Apollo"""

    def __init__(self, app_id, cluster='default', service_locator_url='http://localhost:8080', timeout=10, ip=None,
                 log_config=False, log_store_path='/tmp/apollo_config/'):
        """
        :param app_id: Apollo config AppId
        :param cluster: Apollo config Cluster
        :param config_server_url: Apollo Meta Server URL
        :param timeout: Client notifications Apollo Meta Server timeout
        :param ip: Default local ip
        :param log_config: bool For Debug, Is store App config to local file
        :param log_store_path: Dir for store config file, the file name is apollo release key
        """
        self.service_locator_url = service_locator_url
        self.appId = app_id
        self.cluster = cluster
        self.timeout = timeout
        self.log_config = log_config
        self.log_store_path = log_store_path
        self.stopped = False
        self.ip = None

        self.init_ip(ip)
        self.config_server_urls = self.get_config_services()
        self.callback_funcs = [init_config]

        if not self.config_server_urls:
            raise ValueError('No config services')

        print(f"config server urls {self.config_server_urls}")

        self._stopping = False
        self._cache = {}
        self._long_poll()

    def init_ip(self, ip):
        if ip:
            self.ip = ip
        else:
            import socket
            s = None
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(('8.8.8.8', 53))
                ip = s.getsockname()[0]
            finally:
                if s:
                    s.close()
            self.ip = ip

    # Main method
    def get_value(self, key, default_val=None, namespace='APP_ALL', auto_fetch_on_cache_miss=False):
        if namespace not in self._cache:
            self._cache[namespace] = {}
            # logging.getLogger(__name__).info("Add namespace '%s' to local cache", namespace)
            # This is a new namespace, need to do a blocking fetch to populate the local cache
            self._long_poll()

        if key in self._cache[namespace]:
            return self._cache[namespace][key]
        else:
            if auto_fetch_on_cache_miss:
                return self._cached_http_get(key, default_val, namespace)
            else:
                return default_val

    def add_callback_funcs(self, callback_fun_list):
        if not isinstance(callback_fun_list, (list, tuple)):
            callback_fun_list = [callback_fun_list]
        self.callback_funcs.extend(callback_fun_list)

    # Start the long polling loop. Two modes are provided:
    # thread mode (default), create a worker thread to do the loop. Call self.stop() to quit the loop
    def start(self, catch_signals=True):
        # First do a blocking long poll to populate the local cache, otherwise we may get racing problems
        if len(self._cache) == 0:
            self._long_poll()
        if catch_signals:
            import signal
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            signal.signal(signal.SIGABRT, self._signal_handler)
        t = threading.Thread(target=self._listener, daemon=True)
        t.start()

    def stop(self):
        self._stopping = True
        # logging.getLogger(__name__).info("Stopping listener...")

    def _cached_http_get(self, key, default_val, namespace='application'):
        url = f'{self.choose_server_url()}/configfiles/json/{self.appId}/{self.cluster}/{namespace}?ip={self.ip}'
        r = requests.get(url)
        if r.ok:
            data = r.json()
            self._cache[namespace] = data
            # logging.getLogger(__name__).info('Updated local cache for namespace %s', namespace)
        else:
            data = self._cache[namespace]

        if self.log_config:
            self.write_config_to_file(self._cache, 'cached_config')

        if key in data:
            return data[key]
        else:
            return default_val

    def _uncached_http_get(self, namespace='APP_ALL'):
        url = f'{self.choose_server_url()}/configs/{self.appId}/{self.cluster}/{namespace}?ip={self.ip}&sk=true'
        print(f'request url {url}')
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            self._cache[namespace] = data['configurations']
            release_key = data['releaseKey']
            # logging.getLogger(__name__).info('Updated local cache for namespace %s release key %s: %s',
            #                                  namespace, data['releaseKey'],
            #                                  repr(self._cache[namespace]))
            if self.log_config:
                self.write_config_to_file(self._cache, release_key)
            if self.callback_funcs:
                for fun in self.callback_funcs:
                    if callable(fun):
                        fun(self._cache[namespace])

    def choose_server_url(self):
        if not self.config_server_urls:
            return None
        return random.choice(self.config_server_urls)

    def _signal_handler(self, signal, frame):
        # logging.getLogger(__name__).info('You pressed Ctrl+C!')
        self._stopping = True

    def get_config_services(self):
        url = f'{self.service_locator_url}/services/config?appId={self.appId}'
        r = requests.get(url=url, timeout=(self.timeout, self.timeout))
        if r.status_code != 200:
            raise SystemError()
        data = r.json()
        urls = [d['homepageUrl'] for d in data]
        return [u[:-1] if str(u).endswith('/') else u for u in urls]

    def _long_poll(self):
        self._uncached_http_get()

    def _listener(self):
        # logging.getLogger(__name__).info('Entering listener loop...')
        while not self._stopping:
            self._long_poll()

        # logging.getLogger(__name__).info("Listener stopped!")
        self.stopped = True

    def write_config_to_file(self, content, release_key):
        """把内容写入到本地文件中方便进行debug调试"""
        if not os.path.isdir(self.log_store_path):
            os.mkdir(self.log_store_path)
        file_path = os.path.join(self.log_store_path, release_key)
        with open(file_path, 'w') as f:
            if isinstance(content, dict):
                yaml.dump(content, f)
            else:
                f.write(content)


class ApolloAdapter:
    client: ApolloClient = None

    def init(self):
        app_id = config.get_env('APOLLO_APP_ID')
        if app_id:
            apollo_locator_url = config.get_env('APOLLO_LOCATOR_URL')
            if not apollo_locator_url:
                raise ValueError('APOLLO_LOCATOR_URL is not set')

            self.client = ApolloClient(
                app_id=app_id,
                cluster="default",
                service_locator_url=apollo_locator_url
            )
            self.client.start()


def init():
    apollo.init()


apollo = ApolloAdapter()
