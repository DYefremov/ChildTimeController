import datetime
import os
import time

from threading import Thread

from gi.repository import GLib

from . import Gtk
from ..service.commons import get_config, get_users_list, get_default_config, Day, run_idle, User, ActiveDay, \
    write_config, get_current_user_name, get_logger, get_before_consumed

UI_RESOURCES_PATH = "app/ui/" if os.path.exists("app/ui/") else "/usr/share/child-time-controller/app/ui/"


class MainAppWindow:
    _AUTOSTART_ICON_TEXT = "\nX-MATE-Autostart-enabled=true\nX-GNOME-Autostart-enabled=true\n"

    def __init__(self):
        handlers = {"on_user_switch_state": self.on_user_switch_state,
                    "on_user_changed": self.on_user_changed,
                    "on_save": self.on_save,
                    "on_about": self.on_about,
                    "on_close_window": self.on_close}

        builder = Gtk.Builder()
        builder.add_from_file(UI_RESOURCES_PATH + "main_app_window.glade")
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

        auto_start = self._auto_start_switch.get_active()
        self._config[user_name] = User(name=user_name,
                                       active_days=days,
                                       session_duration=self._duration_spin_button.get_value(),
                                       timeout=self._pause_spin_button.get_value(),
                                       auto_start=auto_start)
        write_config(self._config)
        self.set_auto_start(auto_start, user_name)

    def on_user_switch_state(self, switch, state):
        self._sessions_main_box.set_sensitive(state)

    def show(self):
        self._main_window.show()

    def on_close(self, window, event):
        self._main_window.destroy()

    def on_about(self, item):
        builder = Gtk.Builder()
        builder.add_objects_from_file(UI_RESOURCES_PATH + "dialogs.glade", ("about_dialog",))
        dialog = builder.get_object("about_dialog")
        dialog.set_transient_for(self._main_window)
        dialog.run()
        dialog.destroy()

    def set_auto_start(self, start, user_name):
        icon_file_path = "/home/{}/.config/autostart/child-time-controller.desktop".format(user_name)
        if start:
            with open(icon_file_path, "w") as d_file:
                with open("/usr/share/applications/child-time-controller.desktop", "r") as icon_file:
                    lines = icon_file.readlines()
                    lines.append(self._AUTOSTART_ICON_TEXT)
                    d_file.writelines(lines)
        else:
            if os.path.exists(icon_file_path):
                os.remove(icon_file_path)


class LockWindow:
    _UPDATE_BAR_INTERVAL = 5

    def __init__(self):
        handlers = {"on_lock_exit": self.on_lock_exit}

        builder = Gtk.Builder()
        builder.add_objects_from_file(UI_RESOURCES_PATH + "dialogs.glade", ("lock_window",))
        builder.connect_signals(handlers)
        self._window = builder.get_object("lock_window")
        self._level_bar = builder.get_object("level_bar")

    @run_idle
    def show(self, duration=None):
        print("Locked!")
        self._window.fullscreen()
        self._window.show()
        self.init_level_bar(duration)
        if duration:
            self.show_duration(duration)

    def init_level_bar(self, duration):
        value = duration if duration else 1
        self._level_bar.set_max_value(value)
        self._level_bar.set_value(value)

    @run_idle
    def hide(self):
        print("Unlocked!")
        self._window.hide()

    def on_lock_exit(self, *args):
        self._window.destroy()

    def show_duration(self, duration):
        if duration < 1:
            return

        def update_bar_value():
            nonlocal duration
            duration -= self._UPDATE_BAR_INTERVAL
            self._level_bar.set_value(duration)
            return duration > 0

        GLib.timeout_add_seconds(self._UPDATE_BAR_INTERVAL, update_bar_value)


class StatusIcon:
    _task_active = False

    def __init__(self):
        handlers = {"on_exit": self.on_exit,
                    "on_settings": self.on_settings,
                    "on_status_icon_popup_menu": self.on_status_icon_popup_menu}

        builder = Gtk.Builder()
        builder.add_objects_from_file(UI_RESOURCES_PATH + "dialogs.glade", ("status_icon", "status_icon_menu"))
        builder.connect_signals(handlers)
        self._status_icon = builder.get_object("status_icon")
        self._lock_window = LockWindow()
        self._full_time = 0
        self._duration = 0
        self._timeout = 0
        self._total_consumed = 0
        self._current_day = Day.Mon.value
        self._current_user = ""
        self._logger = get_logger("m", 120)

    @run_idle
    def start_service(self):
        if self._task_active:
            return

        config = get_config()
        self._current_user = get_current_user_name()
        user = config.get(self._current_user, None)

        if not user:
            return

        user = User(*user)
        if not user.auto_start:
            return

        self._current_day = Day(datetime.datetime.now().weekday()).name
        active_day = list(filter(lambda d: d[0] == self._current_day, user.active_days))
        if not active_day:
            return

        self._full_time = int(active_day[0][1])
        self._duration = int(user.session_duration)
        self._timeout = int(user.timeout)
        self._total_consumed = get_before_consumed(self._current_user, active_day)

        if self._total_consumed >= self._full_time:
            Thread(target=self.lock_with_timeout, args=(None, 5), daemon=True).start()
            return
        else:
            self._task_active = True
            # We set how often the log file will be rewritten
            self._logger.handlers[0].set_interval(self._duration)
            Thread(target=self.do_task, daemon=True).start()

    def show(self):
        self.start_service()
        Gtk.main()

    @run_idle
    def on_exit(self, item):
        self._task_active = False
        self._lock_window.on_lock_exit()
        Gtk.main_quit()

    def do_task(self):
        """ Test!!! """
        consumed = 0
        while self._task_active and self._total_consumed < self._full_time:
            consumed += 1
            if consumed > self._duration:
                self.lock(self._timeout * 60)
                time.sleep(self._timeout * 60)
                consumed = 0
                if self._total_consumed < self._full_time:
                    self.unlock()

            self._total_consumed += 1
            self._logger.info("{}:{}:{}".format(self._current_user, self._current_day, self._total_consumed))
            time.sleep(60)

        self.lock()

    @run_idle
    def lock(self, duration=None):
        self._lock_window.show(duration)

    def lock_with_timeout(self, duration=None, timeout=None):
        if timeout:
            time.sleep(timeout)
        self.lock(duration)

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
