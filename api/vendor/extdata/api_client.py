import logging
import os

import requests
import urllib3

urllib3.disable_warnings()

log = logging.getLogger(__name__)


class ApiError(Exception):
    code: str = None
    msg: str = None

    def __init__(self, code, msg):
        self.code = code
        self.msg = msg


def runtime_env():
    return os.environ.get("RUNTIME_ENV")


def get_api_base_url():
    return os.environ.get("TOOL_API_BASE_URL", f'http://etna.{runtime_env()}.svc.cluster.local')


def api_url(url):
    return get_api_base_url() + url


class ToolApiClient:

    def post(self, url, *args, **kwargs):
        return self.check_raise_status(
            requests.post(api_url(url), verify=False, *args, **kwargs)
        )

    def get(self, url, *args, **kwargs):
        return self.check_raise_status(
            requests.get(api_url(url), verify=False, *args, **kwargs)
        )

    def check_raise_status(self, res):
        if res.status_code != 200:
            raise Exception()
        j = res.json()
        if 'code' in j and j['code'] != '200':
            raise ApiError(j['code'], j['msg'])
        return res
