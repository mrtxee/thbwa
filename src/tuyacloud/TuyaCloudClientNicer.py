"""
    Tuya Cloud Client Python package
    based on http-API for Tuya IoT Development Platform

    Dev. Artem Mironov
    For more info see https://github.com/mrtxee/tuyacloud

    Initiation of class object:
        tcc = tuyacloud.TuyaCloudClientNicer(
            ACCESS_ID       = 'XXXXXXXXXXXXXX',
            ACCESS_SECRET   = 'XXXXXXXXXXXXXX',
            UID             = 'XXXXXXXXXXXXXX',
            ENDPOINT_URL    = 'XXXXXXXXXXXXXX'
        )

    TuyaCloudClientNicer is an extension over TuyaCloudClient. It provides just the same methods, but brings
    more significant data in responses, cleaned from meta. Usage of TuyaCloudClientNicer class is preferable
    for the ost cases. See full list of methods in TuyaCloudClient class description.
"""

from .TuyaCloudClient import *


class TuyaCloudClientNicer(TuyaCloudClient):
    def __metada_cut_decorator(func):  # type: ignore
        def decorate(self, *args, **kwargs):
            response = func(self, *args, **kwargs)  # type: ignore
            if response['success']:
                response = response['result']
            return response

        return decorate

    @__metada_cut_decorator  # type: ignore
    def get_device_information(self, device_id=None):
        return super().get_device_information(device_id)

    @__metada_cut_decorator  # type: ignore
    def get_device_details(self, device_id=None):
        return super().get_device_details(device_id)

    @__metada_cut_decorator  # type: ignore
    def get_device_logs(self, device_id=None):
        return super().get_device_logs(device_id)

    @__metada_cut_decorator  # type: ignore
    def get_device_functions(self, device_id=None):
        return super().get_device_functions(device_id)

    @__metada_cut_decorator  # type: ignore
    def get_device_specifications(self, device_id=None):
        return super().get_device_specifications(device_id)

    @__metada_cut_decorator  # type: ignore
    def get_device_status(self, device_id=None):
        return super().get_device_status(device_id)

    @__metada_cut_decorator  # type: ignore
    def get_category_instruction(self, category=None):
        return super().get_category_instruction(category)

    @__metada_cut_decorator  # type: ignore
    def get_home_data(self, home_id=None):
        return super().get_home_data(home_id)

    @__metada_cut_decorator  # type: ignore
    def get_home_rooms(self, home_id=None):
        return super().get_home_rooms(home_id)

    @__metada_cut_decorator  # type: ignore
    def get_home_devices(self, home_id=None):
        return super().get_home_devices(home_id)

    @__metada_cut_decorator  # type: ignore
    def get_home_members(self, home_id=None):
        return super().get_home_members(home_id)

    @__metada_cut_decorator  # type: ignore
    def get_room_devices(self, home_id=None, room_id=None):
        return super().get_room_devices(home_id, room_id)

    @__metada_cut_decorator  # type: ignore
    def get_user_homes(self, user_id=None):
        return super().get_user_homes(user_id)

    @__metada_cut_decorator  # type: ignore
    def get_user_devices(self, user_id=None):
        return super().get_user_devices(user_id)

    @__metada_cut_decorator  # type: ignore
    def get_category_list(self):
        return super().get_category_list()

    @__metada_cut_decorator  # type: ignore
    def get_remote_controls(self, device_id=None):
        return super().get_remote_controls(device_id)

    @__metada_cut_decorator  # type: ignore
    def get_remote_control_keys(self, device_id=None, remote_id=None):
        return super().get_remote_control_keys(device_id, remote_id)

    @__metada_cut_decorator  # type: ignore
    def send_remote_control_command(self, device_id=None, remote_id=None, command=None):
        return super().send_remote_control_command(device_id, remote_id, command)

    # @__metada_cut_decorator  # type: ignore
    # def exec_device_command(self, device_id=None, commands=None):
    #     return super().exec_device_command(device_id, commands)

