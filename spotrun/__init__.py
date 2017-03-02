import logging


logger = logging.getLogger('spotrun')
formatter = logging.Formatter(
    fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

level = 'INFO'

if level == 'INFO':
    logger.setLevel(logging.INFO)
elif level == 'DEBUG':
    logger.setLevel(logging.DEBUG)
