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
        self._main_dialog.show()

    def hide_settings_dialog(self):
        self._main_dialog.hide()

    def _init_ui(self):
        builder = Gtk.Builder()
        builder.add_from_file("ui/main.glade")
        self._main_dialog = builder.get_object("main_window")
        # init ui elements
        self._users_box = builder.get_object("users_box")
        self._users_list_store = builder.get_object("users_list_store")
        self._main_box = builder.get_object("main_box")
        self._data_box = builder.get_object("data_box")
        self._session_duration = builder.get_object("session_duration")
        self._pause_between_sessions = builder.get_object("pause_between_sessions")
        self._auto_start = builder.get_object("auto_start")
        self._active_days = [builder.get_object("sun_box"), builder.get_object("mon_box"),
                             builder.get_object("tue_box"), builder.get_object("wed_box"),
                             builder.get_object("thu_box"), builder.get_object("fri_box"),
                             builder.get_object("sat_box")]
        handlers = {
            "on_about_menu_item_activate": on_about_dialog,
            "on_users_box_changed": self.on_users_box_changed,
            "on_apply_button_clicked": self.on_apply_button_clicked,
            "on_close_clicked": lambda *args: self._main_dialog.destroy()
        }

        builder.connect_signals(handlers)
        self.set_settings()

    def _init_users_box(self):
        users_list = get_users_list()
        for u in users_list:
            self._users_list_store.append([u])

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
        print(self.get_current_user_name())

    def get_current_user_name(self):
        return self._users_list_store.get_value(self._users_box.get_active_iter(), 0)

    def on_apply_button_clicked(self, *args):
        if is_confirmed():
            write_settings(User(self.get_current_user_name(),
                                self.get_active_days(),
                                self._session_duration.get_value(),
                                self._pause_between_sessions.get_value(),
                                self._auto_start.get_active()))
            print(read_settings())

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
