import hashlib
import hmac
import json
import logging
import time
import requests
from .TuyaCloudClientExceptions import *


class TuyaCloudClient:
    def __init__(self, ENDPOINT_URL: str, ACCESS_ID: str, ACCESS_SECRET: str, UID: str):
        self.ENDPOINT_URL = ENDPOINT_URL
        self.ACCESS_ID = ACCESS_ID
        self.ACCESS_SECRET = ACCESS_SECRET
        self.UID = UID
        self.token = None
        self.logger = logging.getLogger(__name__)
        # Attempt to connect to cloud and get token
        self.token = self.__update_token()

    def __update_token(self):
        # Get OAuth Token from tuyaPlatform
        # GET: /v1.0/token
        # https://developer.tuya.com/en/docs/cloud/6c1636a9bd?id=Ka7kjumkoa53v
        self.token = None
        response = self.__send_request('v1.0/token?grant_type=1')

        if not response['success']:
            self.logger.debug("Cloud __update_token(). " + str(response['msg']))

        self.token = response['result']['access_token']
        return self.token

    def __send_request(self, uri, action='GET', post=None, recursive=False) -> dict:
        # Build URL and Header
        url = "https://%s/%s" % (self.ENDPOINT_URL, uri)
        headers = {}
        body = {}
        if action == 'POST':
            body = json.dumps(post)
            headers['Content-type'] = 'application/json'
        else:
            action = 'GET'
        now = int(time.time() * 1000)
        headers = dict(list(headers.items()) + [('Signature-Headers', ":".join(headers.keys()))]) if headers else {}
        if self.token is None:
            payload = self.ACCESS_ID + str(now)
            headers['secret'] = self.ACCESS_SECRET
        else:
            payload = self.ACCESS_ID + self.token + str(now)

        payload += ('%s\n' % action +  # HTTPMethod
                    hashlib.sha256(
                        bytes((body or "").encode('utf-8'))).hexdigest() + '\n' +  ##type: ignore Content-SHA256
                    ''.join(['%s:%s\n' % (key, headers[key])  # Headers
                             for key in headers.get("Signature-Headers", "").split(":")
                             if key in headers]) + '\n' +
                    '/' + url.split('//', 1)[-1].split('/', 1)[-1])
        # Sign Payload
        signature = hmac.new(
            self.ACCESS_SECRET.encode('utf-8'),
            msg=payload.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest().upper()

        # Create Header Data
        headers['client_id'] = self.ACCESS_ID
        headers['sign'] = signature
        headers['t'] = str(now)
        headers['sign_method'] = 'HMAC-SHA256'

        if self.token is not None:
            headers['access_token'] = self.token
        self.logger.debug('Request URL: %s', url)
        # Send Request to Cloud and Get Response
        if action == 'GET':
            response = requests.get(url, headers=headers)
            self.logger.debug("GET: response code=%d text=%s token=%s", response.status_code, response.text, self.token)
        else:
            self.logger.debug("POST: URL=%s HEADERS=%s DATA=%s", url, headers, body)
            response = requests.post(url, headers=headers, data=body)

        # Check to see if token is expired
        if "token invalid" in response.text:
            if recursive is True:
                self.logger.debug("Failed 2nd attempt to renew token - Aborting")
                return {}
            self.logger.debug("Token Expired - Try to renew")
            token = self.__update_token()
            if "err" in token:
                self.logger.debug("Failed to renew token")
                return {}
            else:
                return self.__send_request(uri, action, post, True)

        try:
            response_dict = json.loads(response.content.decode())
        except Exception:
            try:
                response_dict = json.loads(response.content)
            except Exception:
                raise TuyaCloudClientException("Missing Tuya Cloud Key or Secret")
        # Check to see if token is expired
        return response_dict

    def get_device_information(self, device_id=None):
        """
        Get Device Information
        GET: /v1.1/iot-03/devices/{device_id}
        "result": {
            ... "lat": "59.9494",
            "lon": "30.2677",
            "name": "Прихожая μ-7",
            "icon": "smart/device_icon/eu1573240497078AokHW/bf0b36761084b6c12a6dku163725363408970.png",
            "owner_id": "14400180", - home_id ...
        }
        """
        if not device_id:
            raise TuyaCloudClientException("Missing Function Parameters")

        uri = 'v1.1/iot-03/devices/%s' % device_id
        return self.__send_request(uri=uri)
        # return self._getdevice(param='',  deviceid=device_id, ver='v1.1')

    def get_device_details(self, device_id=None):
        """
        Get device details
        GET: /v1.0/devices/{device_id}
        gets less data fields than get_device_information()
        """
        if not device_id:
            raise TuyaCloudClientException("Missing Function Parameters")

        uri = 'v1.0/devices/%s' % device_id
        return self.__send_request(uri=uri)

    def get_device_functions(self, device_id=None):
        """
        GET: /v1.0/devices/{device_id}/functions
        Get the instruction set by device
        """
        if not device_id:
            raise TuyaCloudClientException("Missing Function Parameters")

        uri = 'v1.0/devices/%s/functions' % device_id
        return self.__send_request(uri=uri)

    def get_device_specifications(self, device_id=None):
        """
        GET: /v1.0/devices/{device_id}/specifications
        Get the device’s specifications and properties (including instruction set and status set)
        """
        if not device_id:
            raise TuyaCloudClientException("Missing Function Parameters")

        uri = 'v1.0/devices/%s/specifications' % device_id
        return self.__send_request(uri=uri)

    def get_device_status(self, device_id=None):
        """
        GET: /v1.0/devices/{device_id}/status
        Get the latest device status
        """
        if not device_id:
            raise TuyaCloudClientException("Missing Function Parameters")

        uri = 'v1.0/devices/%s/status' % device_id
        return self.__send_request(uri=uri)


    def exec_device_command(self, device_id=None, commands=None):
        """
        Send instructions to the device
        POST: /v1.0/devices/{device_id}/commands
        """
        if not device_id or not commands:
            raise TuyaCloudClientException("Missing Function Parameters")

        uri = 'v1.0/devices/%s/commands' % device_id
        response_dict = self.__send_request(uri, action='POST', post=commands)

        # if not response_dict['success']:
        #     self.logger.debug("Error from Tuya Cloud: %r", response_dict['msg'])
        return response_dict

    def get_device_logs(self, device_id=None):
        """
        Query device logs
        GET: /v1.0/devices/{device_id}/logs

        # https://developer.tuya.com/en/docs/cloud/8eac85909d?id=Kalmcozgt7nl0
        # GET: /v1.0/iot-03/devices/{device_id}/report-logs
        # Query device status report log
        """
        if not device_id:
            raise TuyaCloudClientException("Missing Function Parameters")

        # uri = 'v1.0/devices/%s/logs' % device_id
        result = {'result': 'method is under maintainse',
                  'msg': 'make yo ass into work launch it'
                  }
        # return self.__send_request(uri=uri)
        return result

    def get_category_instruction(self, category=None):
        """
        Get the instruction set by category
        /v1.0/functions/{category}
        """
        if not category:
            raise TuyaCloudClientException("Missing Function Parameters")

        uri = 'v1.0/functions/' % category
        return self.__send_request(uri=uri)

    def get_home_data(self, home_id=None):
        """
        Search Family ~ get home data
        eg. {
            "result": {
                "lon": 120.5,
                "name": "Ming Mings Family",
                "home_id": 318312,
                "lat": 30.16,
                "geo_name": "Hangzhou City, Tuya Smart"
            },
        }        
        GET: /v1.0/homes/{home_id}
        https://developer.tuya.com/en/docs/cloud/0dbe66fef6?id=Kawfjdzu0dava
        """
        if not home_id:
            raise TuyaCloudClientException("Missing Function Parameters")

        uri = 'v1.0/homes/%s' % home_id
        return self.__send_request(uri=uri)

    def get_home_rooms(self, home_id=None):
        """
        Query Room List
        { 
        "geo_name": "Hangzhou Grand Center", 
        "home_id": 337403, 
        "lat": 30.302553689454005, 
        "lon": 120.0640923396687, 
        "name": "Test Home" 
        "rooms": [ 
            { "name":"Living Room", "room_id": 587609 }, 
            { "name":"Master Bedroom", "room_id": 587610 }, 
            { "name": "Second Bedroom", "room_id": 587611 } 
            ] 
        }
        GET: /v1.0/homes/{home_id}/rooms
        https://developer.tuya.com/en/docs/cloud/5a2fe10caa?id=Kawfjg9hodgdw
        """
        if not home_id:
            raise TuyaCloudClientException("Missing Function Parameters")

        uri = 'v1.0/homes/%s/rooms' % home_id
        return self.__send_request(uri=uri)

    def get_home_devices(self, home_id=None):
        """
        Query Devices under Home
        GET: /v1.0/homes/{home_id}/devices
        """
        if not home_id:
            raise TuyaCloudClientException("Missing Function Parameters")

        uri = 'v1.0/homes/%s/devices' % home_id
        return self.__send_request(uri=uri)

    def get_home_members(self, home_id=None):
        """
        Query Home Members
        GET: /v1.0/homes/{home_id}/members
        """
        if not home_id:
            raise TuyaCloudClientException("Missing Function Parameters")

        uri = 'v1.0/homes/%s/members' % home_id
        return self.__send_request(uri=uri)

    def get_room_devices(self, home_id=None, room_id=None):
        """
        Query family room equipment
        GET: /v1.0/homes/{home_id}/rooms/{room_id}/devices
        https://developer.tuya.com/en/docs/cloud/23ecef19df?id=Kawfjh0l67rd9
        """
        if not home_id:
            raise TuyaCloudClientException("Missing Function Parameters")
        if not room_id:
            raise TuyaCloudClientException("Missing Function Parameters")

        uri = 'v1.0/homes/%s/rooms/%s/devices' % (home_id, room_id)
        return self.__send_request(uri=uri)

    def get_category_list(self):
        '''
        Get Category List
        GET: /v1.0/iot-03/device-categories
        '''
        uri = 'v1.0/iot-03/device-categories'
        return self.__send_request(uri=uri)

    def get_user_homes(self, user_id=None):
        """
        Query User Home List
        GET: /v1.0/users/{uid}/homes
        """
        if not user_id:
            user_id = self.UID
        if not user_id:
            raise TuyaCloudClientException("Missing Function Parameters")

        uri = 'v1.0/users/%s/homes' % user_id
        return self.__send_request(uri=uri)

    def get_user_devices(self, user_id=None):
        """
        Get a list of devices under a specified user
        GET: /v1.0/users/{uid}/devices
        """
        if not user_id:
            user_id = self.UID
        if not user_id:
            raise TuyaCloudClientException("Missing Function Parameters")

        uri = 'v1.0/users/%s/devices' % user_id
        return self.__send_request(uri=uri)

    # other methods
    # should do tests on it
    def sendcommand(self, deviceid=None, commands=None):
        """
        Send a command to the device
        """
        if deviceid is None or commands is None:
            raise TuyaCloudClientException("Missing Function Parameters")

        uri = 'v1.0/iot-03/devices/%s/commands' % deviceid
        response_dict = self.__send_request(uri, action='POST', post=commands)

        if not response_dict['success']:
            self.logger.debug("Error from Tuya Cloud: %r", response_dict['msg'])
        return response_dict

    def getconnectstatus(self, deviceid=None):
        """
        Get the device Cloud connect status. 
        """
        if deviceid is None:
            raise TuyaCloudClientException("Missing Function Parameters")

        uri = 'v1.0/devices/%s' % deviceid
        response_dict = self.__send_request(uri)

        if not response_dict['success']:
            self.logger.debug("Error from Tuya Cloud: %r" % response_dict['msg'])
        return response_dict["result"]["online"]
