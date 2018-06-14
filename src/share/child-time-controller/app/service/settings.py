import json
import os
import pwd
from collections import namedtuple
from enum import Enum


class Constants(Enum):
    """For constants """
    CONFIG_FILE = "settings.json"


User = namedtuple("User", ["name", "active_days", "session_duration", "timeout", "auto_start"])

ActiveDay = namedtuple("ActiveDay", ["day", "time"])


class Day(Enum):
    Sun = 0
    Mon = 1
    Tue = 2
    Wed = 3
    Thu = 4
    Fri = 5
    Sat = 6


def get_config():
    config_file = Constants.CONFIG_FILE.value

    if not os.path.isfile(config_file) or os.stat(config_file).st_size == 0:
        reset_config()

    with open(config_file, "r") as config_file:
        return json.load(config_file)


def reset_config():
    with open(Constants.CONFIG_FILE.value, "w") as default_config_file:
        json.dump(get_default_settings(), default_config_file)


def write_config(config):
    assert isinstance(config, dict)
    with open(Constants.CONFIG_FILE.value, "w") as config_file:
        json.dump(config, config_file)


def get_default_settings(user_name=None):
    if user_name is None:
        user_name = pwd.getpwuid(os.geteuid()).pw_name

    return {user_name: User(user_name, [ActiveDay(Day(i).name, 2) for i in range(8)], 30, 15, False)}


def get_users_list():
    users_list = []
    for p in pwd.getpwall():
        if p[5].startswith("/home/") and p[6] != "/bin/false":
            users_list.append(p[0])
    return users_list


if __name__ == "__main__":
    pass
