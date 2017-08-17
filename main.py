import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from ui.settings import SettingsDialog


def on_status_popup_menu(menu, event_button, event_time):
    menu.popup(None, None, None, menu, event_button, event_time)


def show_settings_dialog(menu):
    settings_dialog.show_settings_dialog()


def on_exit(menu):
    bl = Gtk.Builder()
    bl.add_from_file("ui/exit_dialog.glade")
    exit_dialog = bl.get_object("exit_dialog")
    resp = exit_dialog.run()
    if resp == Gtk.ResponseType.OK:
        print("The OK button was clicked")
    else:
        print("The exit was clicked")
        exit_dialog.destroy()


handlers = {
    "on_exit": Gtk.main_quit,
    "status_popup_menu": on_status_popup_menu,
    "on_exit_item": on_exit,
    "on_show_item": show_settings_dialog
}

builder = Gtk.Builder()
builder.add_from_file("ui/status.glade")
settings_dialog = SettingsDialog()
builder.connect_signals(handlers)
tryIcon = builder.get_object("status")
builder.connect_signals(handlers)

if __name__ == "__main__":
    Gtk.main()
