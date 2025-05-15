import os
from .base import *
from dotenv import load_dotenv

load_dotenv()

RASPBERRYPI_LOCAL_IP = os.environ["RASPBERRYPI_LOCAL_IP"]

DEBUG = False
ALLOWED_HOSTS = ["housebrain", "127.0.0.1", "localhost", RASPBERRYPI_LOCAL_IP]
