from asyncio.windows_events import NULL
import logging

logger_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger_file_handler = logging.FileHandler(f'{__name__}.log')
# logger_file_handler.setLevel(logging.DEBUG)
logger_file_handler.setFormatter(logger_formatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logger_file_handler)
# logger.info(f"{__file__} updated")
logger_TuyaCloudClient = logging.getLogger('tuyacloud.TuyaCloudClient')
logger_TuyaCloudClient.setLevel(logging.DEBUG)
logger_TuyaCloudClient.addHandler(logger_file_handler)