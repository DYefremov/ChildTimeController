import os
import pickle
import pwd
from enum import Enum
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class Constants(Enum):
    """For constants """
    PATH = "settings.cfg"


PATH = Constants.PATH.value


class Day(Enum):
    Sun = 0
    Mon = 1
    Tue = 2
    Wed = 3
    Thu = 4
    Fri = 5
    Sat = 6


class User:
    __slots__ = ["_name", "_active_days", "_auto_start"]

    def __init__(self, name, active_days, auto_start):
        self._name = name
        self._active_days = active_days
        self._auto_start = auto_start

    def __repr__(self):
        return "User name = " + self._name + "\nActive days = " + str(self._active_days) + "\nAuto start = " + str(
            self._auto_start)

    def get_name(self):
        return self._name

    def get_active_days(self):
        return self._active_days

    def is_auto_start(self):
        return self._auto_start


class ActiveDay:
    __slots__ = ["_day", "_time", "_session_duration", "_timeout"]

    def __init__(self, day, time, session_duration, timeout):
        self._day = day
        self._time = time
        self._session_duration = session_duration
        self._timeout = timeout

    def __repr__(self):
        return str("Day = " + self._day) + \
               " Time = " + str(self._time) + \
               " Session_duration = " + str(self._session_duration) + \
               " Timeout = " + str(self._timeout)

    def get_day(self):
        return self._day

    def get_time(self):
        return self._time

    def get_session_duration(self):
        return self._session_duration

    def get_timeout(self):
        return self._timeout


def write_settings(data):
    with open(PATH, "wb") as file:
        pickle.dump(data, file)


def read_settings():
    with open(PATH, "rb") as file:
        return pickle.load(file)


def get_default_settings():
    user_name = pwd.getpwuid(os.geteuid()).pw_name
    active_days = []
    for i in range(7):
        active_days.append(ActiveDay(Day(i).name, 2, 0.5, 5))
    return User(user_name, active_days, True)


def get_users_list():
    users_list = []
    for p in pwd.getpwall():
        if p[5].startswith("/home/") and p[6] != "/bin/false":
            users_list.append(p[0])
    return users_list


def on_about_dialog(item):
    builder = Gtk.Builder()
    builder.add_from_file("ui/about_dialog.glade")
    dialog = builder.get_object("about_dialog")
    dialog.run()
    dialog.hide()


def is_confirmed():
    """Shows confirmation dialog"""
    builder = Gtk.Builder()
    builder.add_from_file("ui/confirmation_dialog.glade")
    dialog = builder.get_object("confirmation_dialog")
    confirm = dialog.run() == Gtk.ResponseType.OK
    dialog.destroy()
    return confirm


class SettingsDialog:
    def __init__(self):
        # check whether a file exists and write default
        if not os.path.exists(PATH):
            write_settings(get_default_settings())
        self._init_ui()
        self._init_users_box()
        self.response = self._main_dialog.run()
        self._main_dialog.destroy()

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
        self._main_dialog = self._builder.get_object("main_dialog")
        # init ui elements
        self._cancel_button = self._builder.get_object("cancel_button")
        self._apply_button = self._builder.get_object("apply_button")
        self._exit_menu_item = self._builder.get_object("exit_menu_item")
        self._about_menu_item = self._builder.get_object("about_menu_item")
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
            "on_close_menu_item_activate": lambda *args: self._main_dialog.destroy()
        }

        self._builder.connect_signals(handlers)

    def get_settings(self):
        pass

    def set_settings(self):
        pass

    def on_users_box_changed(self, *args):
        return self.get_current_user_name()

    def on_apply_button_clicked(self, *args):
        if is_confirmed():
            user_name = self.get_current_user_name()
            write_settings(User(user_name, self.get_active_days(), self._auto_start.get_active()))
            print(read_settings())

    def get_current_user_name(self):
        """ Get current selected user name """
        tr_iter = self.users_box.get_active_iter()
        if tr_iter is not None:
            model = self.users_box.get_model()
            print(model[tr_iter][0])
            return model[tr_iter][0]
        return ""

    def get_active_days(self):
        active_days = []
        for box in self._active_days:
            day = box.get_children()[0]
            if day.get_active():
                time = box.get_children()[1].get_value_as_int()
                duration = self._session_duration.get_value()
                timeout = self._pause_between_sessions.get_value_as_int()
                active_days.append(ActiveDay(day.get_label(), time, duration, timeout))
        return active_days


if __name__ == "__main__":
    pass
