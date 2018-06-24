import json
import os
import pwd
import logging
import time

from collections import namedtuple
from enum import Enum
from functools import wraps
from logging.handlers import TimedRotatingFileHandler

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

_LOG_FILE = "time_controller.log"
_DATE_FORMAT = "%d-%m-%y %H:%M:%S %w"  # 'w' is current day (0-6)


class ExtTimedRotatingFileHandler(TimedRotatingFileHandler):
    def doRollover(self):
        """ """
        if self.stream:
            self.stream.close()
            self.stream = None
        current_time = int(time.time())
        if os.path.exists(self.baseFilename):
            os.remove(self.baseFilename)

        if not self.delay:
            self.stream = self._open()
        new_rollover_at = self.computeRollover(current_time)
        while new_rollover_at <= current_time:
            new_rollover_at = new_rollover_at + self.interval
        self.rolloverAt = new_rollover_at

    def set_interval(self, interval):
        self.interval = interval


def get_logger(when="m", interval=1):
    logging.basicConfig(level=logging.INFO,
                        # filename=_LOG_FILE,
                        # format="%(asctime)s %(message)s",
                        format="%(message)s",
                        datefmt=_DATE_FORMAT)
    log = logging.getLogger("main_logger")
    log.setLevel(logging.INFO)
    handler = ExtTimedRotatingFileHandler(_LOG_FILE, backupCount=0, when=when, interval=interval)
    log.addHandler(handler)

    return log


def get_before_consumed(user_name, active_day):
    def get_value(val):
        data = val.split(":")
        return data and user_name == data[0] and active_day == active_day

    with open(_LOG_FILE) as file:
        values = list(filter(get_value, file.readlines()))

        return int(max(map(lambda x: int(x.split(":")[2]), values))) if values else 0


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


def write_config(config: dict):
    with open(Constants.CONFIG_FILE.value, "w") as config_file:
        json.dump(config, config_file)


def get_default_config(user_name=None):
    if user_name is None:
        user_name = get_current_user_name()

    return {user_name: User(user_name, [ActiveDay(Day(i).name, 120) for i in range(7)], 30, 15, False)}


def get_current_user_name():
    return pwd.getpwuid(os.geteuid()).pw_name


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


# ******************** # ******************** #


if __name__ == "__main__":
    pass
