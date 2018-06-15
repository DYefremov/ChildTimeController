import json
import os
import pwd
import logging

from collections import namedtuple
from enum import Enum
from functools import wraps
from subprocess import getoutput

from gi.repository import GLib


class Constants(Enum):
    """For constants """
    CONFIG_FILE = "settings.json"


User = namedtuple("User", ["name", "active_days", "session_duration", "timeout", "auto_start"])

ActiveDay = namedtuple("ActiveDay", ["day", "time"])


class Day(Enum):
    Mon = 0
    Tue = 1
    Wed = 2
    Thu = 3
    Fri = 4
    Sat = 5
    Sun = 6


# ******************** Logger ******************** #

LOG_FILE = "/home/dimon/log.log"
DATE_FORMAT = "%d-%m-%y %H:%M:%S %w"  # 'w' is current day (0-6)

logging.Logger("main_logger")
logging.basicConfig(level=logging.INFO,
                    filename=LOG_FILE,
                    # format="%(asctime)s %(message)s",
                    format="%(message)s",
                    datefmt=DATE_FORMAT)


def get_logger():
    return logging.getLogger("main_logger")


def open_log():
    with open(LOG_FILE) as file:
        lines = file.readlines()
        for line in lines:
            print(line)


def log_login():
    """
    Used to redirect logs from 'last'.

    It is necessary because wtmp can be in tmpfs (as at me).
    """
    logger = get_logger()
    with open(LOG_FILE) as file:
        lines = set(file.readlines())
    # logger.info(pwd.getpwuid(os.geteuid()).pw_name)
    out = getoutput("last -R").splitlines()
    sep = str("(")
    end = "\n"
    for line in out:
        if line + end not in lines and sep in line:
            logger.info(line)


# ******************** Config ******************** #

def get_config():
    config_file = Constants.CONFIG_FILE.value

    if not os.path.isfile(config_file) or os.stat(config_file).st_size == 0:
        reset_config()

    with open(config_file, "r") as config_file:
        return json.load(config_file)


def reset_config():
    with open(Constants.CONFIG_FILE.value, "w") as default_config_file:
        json.dump(get_default_config(), default_config_file)


def write_config(config):
    assert isinstance(config, dict)
    with open(Constants.CONFIG_FILE.value, "w") as config_file:
        json.dump(config, config_file)


def get_default_config(user_name=None):
    if user_name is None:
        user_name = pwd.getpwuid(os.geteuid()).pw_name

    return {user_name: User(user_name, [ActiveDay(Day(i).name, 2) for i in range(7)], 30, 15, False)}


def get_users_list():
    users_list = []
    for p in pwd.getpwall():
        if p[5].startswith("/home/") and p[6] != "/bin/false":
            users_list.append(p[0])
    return users_list


# ******************** Others ******************** #


def run_idle(func):
    """ Runs a function with a lower priority """

    @wraps(func)
    def wrapper(*args, **kwargs):
        GLib.idle_add(func, *args, **kwargs)

    return wrapper


def is_in_file(f, text):
    return any(text in line for line in f)


def is_user_in_list(*args):
    """"
       Checking the need for logging for this user(s).

        Need implementation.!!!
       """
    return True


# ******************** # ******************** #


if __name__ == "__main__":
    pass
