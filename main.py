import gi
import subprocess

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from ui.settings import SettingsDialog


def on_status_popup_menu(menu, event_button, event_time):
    menu.popup(None, None, None, menu, event_button, event_time)


def show_settings_dialog(menu):
    if check_permissions():
        SettingsDialog()


def on_exit(menu):
    if check_permissions():
        print("PASS")
        Gtk.main_quit()


def check_permissions():
    out = subprocess.getoutput("gksu -m 'ChildController' 'ls'")
    # Current file name
    res = __file__.split("/")[-1:][0]
    return res in out


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
    Gtk.main()
