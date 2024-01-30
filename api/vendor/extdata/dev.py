# coding: utf-8
from typing import Union, Optional

from vendor.extdata.api_client import ToolApiClient


class DeviceNotExistError(Exception):
    dev_id: str

    def __init__(self, dev_id):
        self.dev_id = dev_id


class Device:
    dev_id: str = None
    product_id: str = None
    name: str = None

    client: ToolApiClient = None

    def __init__(self, dev_id, client: Optional[ToolApiClient]):
        self.dev_id = dev_id
        self.client = client
        self.info()

    def __str__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {
            'dev_id': self.dev_id,
            'product_id': self.product_id
        }

    def info(self):
        r = self.client.get(f'/tools/device/{self.dev_id}')
        data = r.json()
        if 'result' not in data or not data['result']:
            raise DeviceNotExistError(self.dev_id)
        dev_info = data['result']
        self.product_id = dev_info['productId']
        self.name = dev_info['name']

    def diagnose(self, fn_type, *args, **kwargs) -> str or None:
        if fn_type == 'CHECK_OTA_UPGRADE':
            return self.__check_upgrade(*args, **kwargs)
        elif fn_type == 'OTA_FAIL' or fn_type == 'OTA_TIMEOUT':
            return self.__get_ota_error_log(*args, **kwargs)
        else:
            return None

    def __check_upgrade(self, *args, **kwargs):
        r = self.client.post(f'/tools/diagnose/firmwareOtaCheckDiagnose', json={
            'devId': self.dev_id
        })
        data = r.json()
        return data['result']['msg']

    def __get_ota_error_log(self, *args, **kwargs):
        r = self.client.post(f'/tools/diagnose/firmwareOtaFailDiagnose', json={
            'devId': self.dev_id
        })
        data = r.json()
        dg_id = data['result']['dgId']

        r = self.client.get(f'/tools/diagnose/firmwareOtaFailDiagnose/logs', params={
            'dgId': dg_id,
            'devId': self.dev_id,
            'logLevel': 'error',
        })
        data = r.json()
        return data['result']


class MockDevice(Device):

    def info(self):
        self.product_id = 'mock_pid'

    def diagnose(self, fn_type, *args, **kwargs) -> str or None:
        if fn_type == 'CHECK_OTA_UPGRADE':
            return '设备已经是最新版本'
        elif fn_type == 'OTA_FAIL' or fn_type == 'OTA_TIMEOUT':
            return 'failed to malloc memory'
        else:
            return None


class DeviceFactory:
    client = ToolApiClient()

    @classmethod
    def find_dev_by_id(cls, dev_id: str) -> Union[Device, None]:
        if 'mock' == dev_id:
            return MockDevice(dev_id, None)

        try:
            return Device(dev_id, cls.client)
        except DeviceNotExistError:
            return None

# d = DeviceFactory.find_dev_by_id('0707060384f3ebc61b32')
# print(d.diagnose('OTA_FAIL'))
