import os
import pickle
import pwd
from collections import namedtuple
from enum import Enum


class Constants(Enum):
    """For constants """
    PATH = "settings.cfg"


PATH = Constants.PATH.value

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


def write_settings(data):
    with open(PATH, "wb") as file:
        pickle.dump(data, file)


def read_settings():
    # check whether a file exists and write default
    if not os.path.exists(PATH):
        write_settings(get_default_settings())
    with open(PATH, "rb") as file:
        return pickle.load(file)


def get_default_settings():
    user_name = pwd.getpwuid(os.geteuid()).pw_name
    active_days = []
    for i in range(7):
        active_days.append(ActiveDay(Day(i), 2))
    return User(user_name, active_days, 30, 15, False)


def get_users_list():
    users_list = []
    for p in pwd.getpwall():
        if p[5].startswith("/home/") and p[6] != "/bin/false":
            users_list.append(p[0])
    return users_list


if __name__ == "__main__":
    pass
