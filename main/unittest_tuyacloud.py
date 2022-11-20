import json
import logging
import tuyacloud
import os
os.system('cls' if os.name == 'nt' else 'clear')

logger_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger_file_handler = logging.FileHandler(f'{__file__}.log')
logger_file_handler.setLevel(logging.DEBUG)
logger_file_handler.setFormatter(logger_formatter)
logger_stream_handler = logging.StreamHandler()
logger_stream_handler.setLevel(logging.ERROR)
logger_stream_handler.setFormatter(logger_formatter)
logger_TuyaCloudClient = logging.getLogger('tuyacloud.TuyaCloudClient')
logger_TuyaCloudClient.setLevel(logging.DEBUG)
logger_TuyaCloudClient.addHandler(logger_stream_handler)
logger_TuyaCloudClient.addHandler(logger_file_handler)
logger_TuyaCloudClient.info("No custom logger provided. Load default logger is on")

device_id="bfebd1dd8fb1b06ddaw6b3"
home_id = "14400180"
room_id = "21077755"

tcc = tuyacloud.TuyaCloudClientNicer(
    ACCESS_ID      = "4fuehnegqrfqspnpymn9", 
    ACCESS_SECRET  = "5bb653adee024441aa74fc49f50b6727",
    UID            = "eu1573240497078AokHW",
    ENDPOINT_URL   = "openapi.tuyaeu.com"
)

'''
main_user_settings
	user_id			FOREIGN KEY REFERENCES auth_user (id) DEFERRABLE INITIALLY DEFERRED
    access_id     	VARCHAR
    access_secret	VARCHAR
    uid           	VARCHAR
    endpoint_url   	VARCHAR
'''


result = tcc.get_home_members(home_id)
print("get_home_members:\n", json.dumps(result, indent=3, ensure_ascii=False) )
'''
result = tcc.get_home_devices(home_id)
print("get_home_devices:\n", json.dumps(result, indent=3, ensure_ascii=False) )

result = tcc.get_device_details(device_id)
print("get_device_details:\n", json.dumps(result, indent=3, ensure_ascii=False) )

result = tcc.get_user_devices()
print("get_user_devices:\n", json.dumps(result, indent=3, ensure_ascii=False) )

result = tcc.get_home_rooms(home_id)
print("get_home_rooms:\n", json.dumps(result, indent=3, ensure_ascii=False) )

result = tcc.get_all_devices()
print("get_all_devices:\n", json.dumps(result, indent=3, ensure_ascii=False) )

result = tcc.get_home_data(home_id)
print("get_home_data:\n", json.dumps(result, indent=3, ensure_ascii=False) )

result = tcc.get_room_devices(home_id, room_id)
print("get_room_devices:\n", json.dumps(result, indent=3, ensure_ascii=False) )

result = tcc.get_user_homes()
print("get_user_homes:\n", json.dumps(result, indent=3, ensure_ascii=False) )

result = tcc.get_device_information(device_id)
print("get_device_information:\n", json.dumps(result, indent=3, ensure_ascii=False) )

result = tcc.get_category_list()
print("get_category_list:\n", json.dumps(result, indent=3, ensure_ascii=False) )

'''

'''
mt.write_devices_csv_file(tcc)

'''

'''
# Send Command - Turn on switch
commands = {
    "commands": [
        {"code": "switch_1", "value": True},
        {"code": "countdown_1", "value": 0},
    ]
}
print("Sending command...")
result = tcc.sendcommand(id,commands)
print("Results\n:", result)
'''