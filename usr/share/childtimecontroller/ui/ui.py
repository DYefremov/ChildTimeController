import datetime
import subprocess
import threading
import time

from usr.share.childtimecontroller.settings import get_users_list, read_settings, write_settings, User, ActiveDay, Day
from . import Gtk


class StatusIcon:
    def __init__(self):
        handlers = {
            "status_popup_menu": self.on_status_popup_menu,
            "on_show_item": self.show_settings_dialog,
            "on_exit_item": self.on_exit,
        }

        builder = Gtk.Builder()
        builder.add_from_file("ui/status.glade")
        builder.connect_signals(handlers)
        self.try_icon = builder.get_object("status_icon")

    def on_status_popup_menu(self, menu, event_button, event_time):
        menu.popup(None, None, None, menu, event_button, event_time)

    def show_settings_dialog(self, item):
        # if check_permissions():
        SettingsDialog()

    def on_exit(self, item):
        # if check_permissions():
        #     print("PASS")
        Gtk.main_quit()


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


def check_permissions():
    out = subprocess.getoutput("gksu -m 'ChildController' 'ls'")
    # Current file name
    res = __file__.split("/")[-1:][0]
    return res in out


class TimeService(threading.Thread):
    def __init__(self, durations):
        super(TimeService, self).__init__()
        self._durations = durations
        self.total_time = 0

    def run(self):
        start_time = time.time()
        session_duration = self._durations[1]
        timeout = self._durations[2]
        while self.total_time < self._durations[0] * 10:
            time.sleep(1)
            if time.time() - start_time > session_duration:
                self.total_time += time.time() - start_time
                time.sleep(timeout)
                self.total_time -= timeout
                if self.total_time > self._durations[0] * 5:
                    pass
                    # tryIcon.set_from_icon_name("face-angry")
        # tryIcon.set_from_icon_name("face-raspberry")
        print(self.total_time)


def init_service():
    """ Initialize main service """
    st = read_settings()
    for d in st.active_days:
        if d.day == Day(datetime.datetime.now().weekday()):
            start_time_service(d.time, st.session_duration, st.timeout)


def start_time_service(*args):
    """ Starts tracks time service. """
    service = TimeService(args)
    service.start()
    print(args)


def start_ui():
    StatusIcon()
    Gtk.main()


if __name__ == "__main__":
    pass
