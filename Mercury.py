"""
import logging


formatter = logging.Formatter("%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s")

handler_critic = logging.FileHandler("critic.log", mode="a", encoding="utf-8")
handler_info = logging.FileHandler("info.log", mode="a", encoding="utf-8")

handler_critic.setFormatter(formatter)
handler_info.setFormatter(formatter)

handler_info.setLevel(logging.INFO)
handler_critic.setLevel(logging.CRITICAL)

logger = logging.getLogger("nom_programme")
logger.setLevel(logging.INFO)
logger.addHandler(handler_critic)
logger.addHandler(handler_info)

logger.debug('Debug error')
logger.info('INFO ERROR')
logger.critical('INFO ERROR2')

"""
"""
import signal
import sys
import time
import threading

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C')
forever = threading.Event()
forever.wait()
