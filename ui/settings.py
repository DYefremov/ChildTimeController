import os
import pickle
import pwd
from collections import namedtuple
from enum import Enum

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


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


def on_about_dialog(*args):
    builder = Gtk.Builder()
    builder.add_from_file("ui/main.glade")
    dialog = builder.get_object("about_dialog")
    dialog.run()
    dialog.destroy()


def is_confirmed():
    """Shows confirmation dialog"""
    builder = Gtk.Builder()
    builder.add_from_file("ui/main.glade")
    dialog = builder.get_object("confirmation_dialog")
    confirm = dialog.run() == Gtk.ResponseType.OK
    dialog.destroy()
    return confirm


class SettingsDialog:
    def __init__(self):
        self._init_ui()
        self._init_users_box()
        self.response = self._main_dialog.show_all()

    def hide_settings_dialog(self):
        self._main_dialog.hide()

    def _init_users_box(self):
        users_list = get_users_list()
        self.users_box = self._builder.get_object("users_box")
        self.list = Gtk.ListStore(str)

        for u in users_list:
            self.list.append([u])

        self.users_box.set_model(self.list)
        self.users_box.set_active(0)
        cell = Gtk.CellRendererText()
        self.users_box.pack_start(cell, True)
        self.users_box.add_attribute(cell, "text", 0)

    def _init_ui(self):
        self._builder = Gtk.Builder()
        self._builder.add_from_file("ui/main.glade")
        self._main_dialog = self._builder.get_object("main_window")
        # init ui elements
        self._main_box = self._builder.get_object("main_box")
        self._data_box = self._builder.get_object("main_box")
        self._session_duration = self._builder.get_object("session_duration")
        self._pause_between_sessions = self._builder.get_object("pause_between_sessions")
        self._auto_start = self._builder.get_object("auto_start")
        self._active_days = [self._builder.get_object("sun_box"), self._builder.get_object("mon_box"),
                             self._builder.get_object("tue_box"), self._builder.get_object("wed_box"),
                             self._builder.get_object("thu_box"), self._builder.get_object("fri_box"),
                             self._builder.get_object("sat_box")]
        handlers = {
            "on_about_menu_item_activate": on_about_dialog,
            "on_users_box_changed": self.on_users_box_changed,
            "on_apply_button_clicked": self.on_apply_button_clicked,
            "on_close_clicked": lambda *args: self._main_dialog.destroy()
        }

        self._builder.connect_signals(handlers)
        self.set_settings()

    def get_settings(self):
        pass

    def set_settings(self):
        settings = read_settings()
        self._auto_start.set_active(settings.auto_start)
        self._session_duration.set_value(settings.session_duration)
        self._pause_between_sessions.set_value(settings.timeout)
        for d in settings.active_days:
            box = self._active_days[d.day.value]
            box.get_children()[0].set_active(True)
            button = box.get_children()[1]
            button.set_value(d.time)

    def on_users_box_changed(self, *args):
        name = self.get_current_user_name()
        # if name == "user":
        #     self._main_box.remove(self._data_box)
        # else:
        #     self._main_box.pack_start(self._data_box, True, True, 2)
        return name

    def on_apply_button_clicked(self, *args):
        if is_confirmed():
            write_settings(User(self.get_current_user_name(),
                                self.get_active_days(),
                                self._session_duration.get_value(),
                                self._pause_between_sessions.get_value(),
                                self._auto_start.get_active()))
            print(read_settings())

    def get_current_user_name(self):
        """ Get current selected user name """
        tr_iter = self.users_box.get_active_iter()
        if tr_iter is not None:
            model = self.users_box.get_model()
            return model[tr_iter][0]
        return ""

    def get_active_days(self):
        active_days = []
        for index, box in enumerate(self._active_days):
            day = box.get_children()[0]
            if day.get_active():
                time = box.get_children()[1].get_value_as_int()
                active_days.append(ActiveDay(Day(index), time))
        return active_days


if __name__ == "__main__":
    pass
