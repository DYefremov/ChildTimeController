import datetime
import os
import time

from threading import Thread

from . import Gtk
from ..service.commons import get_config, get_users_list, get_default_config, Day, run_idle, User, ActiveDay, \
    write_config, get_current_user_name

UI_RESOURCES_PATH = "app/ui/" if os.path.exists("app/ui/") else "/usr/share/child-time-controller/app/ui/"


class MainAppWindow:

    def __init__(self):
        handlers = {"on_user_switch_state": self.on_user_switch_state,
                    "on_user_changed": self.on_user_changed,
                    "on_save": self.on_save,
                    "on_close_window": self.on_close}

        builder = Gtk.Builder()
        builder.add_objects_from_file(UI_RESOURCES_PATH + "main_app_window.glade",
                                      ("main_app_window", "users_list_store", "mon_adjustment", "tue_adjustment",
                                       "wed_adjustment", "thu_adjustment", "fri_adjustment", "sat_adjustment",
                                       "sun_adjustment", "duration_adjustment", "pause_adjustment"))
        builder.connect_signals(handlers)

        self._main_window = builder.get_object("main_app_window")
        self._users_list_store = builder.get_object("users_list_store")
        self._user_combo_box = builder.get_object("user_combo_box")
        self._sessions_main_box = builder.get_object("sessions_main_box")
        self._auto_start_switch = builder.get_object("auto_start_switch")
        self._duration_spin_button = builder.get_object("duration_spin_button")
        self._pause_spin_button = builder.get_object("pause_spin_button")
        self._days = {k.name: builder.get_object(str(k.name).lower() + "_check_button") for k in Day}
        self._days_values = {k.name: builder.get_object(str(k.name).lower() + "_spin_button") for k in Day}

        self._init_users()
        self._config = get_config()

    @run_idle
    def _init_users(self):
        users_list = get_users_list()
        for u in users_list:
            self._users_list_store.append([u])
        self._user_combo_box.set_active(0)

    @run_idle
    def on_user_changed(self, box: Gtk.ComboBox):
        user_name = box.get_active_id()
        user = User(*self._config[user_name]) if user_name in self._config else get_default_config(user_name)[user_name]
        self._auto_start_switch.set_active(user.auto_start)

        for d in user.active_days:
            self._days.get(d[0]).set_active(True)
            self._days_values.get(d[0]).set_value(d[1])

        self._duration_spin_button.set_value(user.session_duration)
        self._pause_spin_button.set_value(user.timeout)

    def on_save(self, item):
        user_name = self._user_combo_box.get_active_id()
        days = [ActiveDay(d.get_label(), self._days_values.get(d.get_label()).get_value()) for d in self._days.values()
                if d.get_active()]

        self._config[user_name] = User(name=user_name,
                                       active_days=days,
                                       session_duration=self._duration_spin_button.get_value(),
                                       timeout=self._pause_spin_button.get_value(),
                                       auto_start=self._auto_start_switch.get_active())
        write_config(self._config)

    def on_user_switch_state(self, switch, state):
        self._sessions_main_box.set_sensitive(state)

    def show(self):
        self._main_window.show()

    def on_close(self, window, event):
        self._main_window.destroy()


class LockWindow:

    def __init__(self):
        handlers = {"on_lock_exit": self.on_lock_exit}

        builder = Gtk.Builder()
        builder.add_objects_from_file(UI_RESOURCES_PATH + "main_app_window.glade", ("lock_window",))
        builder.connect_signals(handlers)
        self._window = builder.get_object("lock_window")

    @run_idle
    def show(self):
        print("Locked!")
        self._window.show()

    @run_idle
    def hide(self):
        print("Unlocked!")
        self._window.hide()

    def on_lock_exit(self, *args):
        self._window.destroy()


class StatusIcon:
    _task_active = False

    def __init__(self):
        handlers = {"on_exit": self.on_exit,
                    "on_settings": self.on_settings,
                    "on_status_icon_popup_menu": self.on_status_icon_popup_menu}

        builder = Gtk.Builder()
        builder.add_objects_from_file(UI_RESOURCES_PATH + "main_app_window.glade", ("status_icon", "status_icon_menu"))
        builder.connect_signals(handlers)
        self._lock_window = LockWindow()

        self._status_icon = builder.get_object("status_icon")

    @run_idle
    def start_service(self):
        if self._task_active:
            return

        config = get_config()
        user_name = get_current_user_name()
        user = config.get(user_name, None)

        if not user:
            return

        user = User(*user)
        if not user.auto_start:
            return

        current_day = Day(datetime.datetime.now().weekday()).name
        active_day = list(filter(lambda d: d[0] == current_day, user.active_days))
        if not active_day:
            return

        Thread(target=self.do_task, args=(active_day[0][1], user.session_duration, user.timeout)).start()

    def show(self):
        self.start_service()
        Gtk.main()

    @run_idle
    def on_exit(self, item):
        self._task_active = False
        self._lock_window.on_lock_exit()
        Gtk.main_quit()

    def do_task(self, full_time: int, duration: int, timeout: int):
        """ Test!!! """
        self._task_active = True
        print("Started")

        consumed = 0
        full_time, duration, timeout = int(full_time), int(duration), int(timeout)

        while self._task_active and full_time > 0:
            full_time -= 1
            consumed += 1
            if consumed > duration:
                self.lock()
                time.sleep(timeout)
                full_time -= timeout - 1
                consumed = 0

                if full_time:
                    self.unlock()

            time.sleep(1)
            print(full_time)

        self.lock()

    @run_idle
    def lock(self):
        self._lock_window.show()

    @run_idle
    def unlock(self):
        self._lock_window.hide()

    @staticmethod
    def on_settings(item):
        MainAppWindow().show()

    @staticmethod
    def on_status_icon_popup_menu(menu, event_button, event_time):
        menu.popup(None, None, None, menu, event_button, event_time)


def start_app():
    StatusIcon().show()


if __name__ == "__main__":
    pass
