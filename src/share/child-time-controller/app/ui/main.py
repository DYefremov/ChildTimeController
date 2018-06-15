import concurrent.futures
import os
import time

from threading import Thread

from . import Gtk
from ..service.commons import get_config, get_users_list, get_default_config, Day, run_idle, User

UI_RESOURCES_PATH = "app/ui/" if os.path.exists("app/ui/") else "/usr/share/child-time-controller/app/ui/"


class MainAppWindow:

    def __init__(self):
        handlers = {"on_user_switch_state": self.on_user_switch_state,
                    "on_user_changed": self.on_user_changed,
                    "on_close_window": self.on_close}

        builder = Gtk.Builder()
        builder.add_objects_from_file(UI_RESOURCES_PATH + "main_app_window.glade",
                                      ("main_app_window", "users_list_store", "mon_adjustment", "tue_adjustment",
                                       "wed_adjustment", "thu_adjustment", "fri_adjustment", "sat_adjustment",
                                       "sun_adjustment", "duration_adjustment", "pause_adjustment"))
        builder.connect_signals(handlers)

        self._main_window = builder.get_object("main_app_window")
        self._users_list_store = builder.get_object("users_list_store")
        self._sessions_main_box = builder.get_object("sessions_main_box")
        self._auto_start_switch = builder.get_object("auto_start_switch")
        self._duration_spin_button = builder.get_object("duration_spin_button")
        self._pause_spin_button = builder.get_object("pause_spin_button")
        self._days = {k.name: builder.get_object(str(k.name).lower() + "_check_button") for k in Day}
        self._days_values = {k.name: builder.get_object(str(k.name).lower() + "_spin_button") for k in Day}

        self._init_users()
        self._config = get_config()

    def _init_users(self):
        users_list = get_users_list()
        for u in users_list:
            self._users_list_store.append([u])

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

    def show(self):
        self._window.show()

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

        self._status_icon = builder.get_object("status_icon")

    def start_service(self):
        if self._task_active:
            return

        with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
            self._task_active = True
            text = "Processing: {}\n"
            futures = {executor.submit(self.do_task, text)}
            for future in concurrent.futures.as_completed(futures):
                if not self._task_active:
                    executor.shutdown()
                    return

            self._task_active = False

    def show(self):
        Thread(target=self.start_service, daemon=True).start()
        Gtk.main()

    def on_exit(self, item):
        self._task_active = False
        Gtk.main_quit()

    def do_task(self, message: str):
        counter = 2
        while True:
            counter -= 1
            print(message.format(counter))
            time.sleep(1)
            if counter == 0:
                self.show_lock()
                break

    @staticmethod
    def on_settings(item):
        MainAppWindow().show()

    @staticmethod
    def on_status_icon_popup_menu(menu, event_button, event_time):
        menu.popup(None, None, None, menu, event_button, event_time)

    @staticmethod
    def show_lock():
        print("Done!!!")


def start_app():
    StatusIcon().show()


if __name__ == "__main__":
    pass
