import datetime
import subprocess
import threading
import time

from gi.repository import Gtk

import ui.settings as settings


class TimeService(threading.Thread):
    def __init__(self, durations):
        super(TimeService, self).__init__()
        self._durations = durations
        self.total_time = 0

    def run(self):
        start_time = datetime.datetime.now().timestamp()
        session_duration = self._durations[1]
        timeout = self._durations[2]
        while self.total_time < self._durations[0] * 10:
            time.sleep(1)
            if datetime.datetime.now().timestamp() - start_time > session_duration:
                self.total_time += datetime.datetime.now().timestamp() - start_time
                print(self.total_time)
                time.sleep(timeout)
                self.total_time -= timeout
        print("Done!\n")
        print("Total", self.total_time)


def on_status_popup_menu(menu, event_button, event_time):
    menu.popup(None, None, None, menu, event_button, event_time)


def show_settings_dialog(menu):
    if check_permissions():
        settings.SettingsDialog()


def on_exit(menu):
    if check_permissions():
        print("PASS")
        Gtk.main_quit()


def check_permissions():
    out = subprocess.getoutput("gksu -m 'ChildController' 'ls'")
    # Current file name
    res = __file__.split("/")[-1:][0]
    return res in out


def init_service():
    """ Initialize main service """
    st = settings.read_settings()
    for d in st.active_days:
        if d.day == settings.Day(datetime.datetime.now().weekday()):
            start_time_service(d.time, st.session_duration, st.timeout)


def start_time_service(*args):
    """ Starts tracks time service. """
    service = TimeService(args)
    service.start()
    print(args)


handlers = {
    "status_popup_menu": on_status_popup_menu,
    "on_exit_item": on_exit,
    "on_show_item": show_settings_dialog
}

builder = Gtk.Builder()
builder.add_from_file("ui/status.glade")
builder.connect_signals(handlers)
tryIcon = builder.get_object("status")
builder.connect_signals(handlers)

if __name__ == "__main__":
    init_service()
    Gtk.main()
