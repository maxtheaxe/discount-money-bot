"""
... [Docstring]
"""

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import chromedriver_autoinstaller as cda  # makes it easier on inexperienced users
import twint as tw  # unofficial twit api of sorts, so ppl don't have to set up dev stuff
from playsound import playsound  # for notifying users; optional
from datetime import datetime, timedelta
import time
import random
import signal
import os
import inspect
import sys
import random

CWD = os.path.abspath(os.path.dirname(__file__))

current_folder = os.path.realpath(
    os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))

__all__ = [
    "CWD",
    "current_folder",
    
    "webdriver",
    "EC",
    "By",
    "WebDriverWait",
    "NoSuchElementException",
    "ActionChains",
    "Keys",
    "cda",
    "tw",
    "playsound",
    "datetime",
    "timedelta",
    "time",
    "random",
    "signal",
    "os",
    "inspect",
    "sys",
    "random"
]
