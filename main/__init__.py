import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


def on_status_popup_menu(menu, event_button, event_time):
    menu.popup(None, None, None, menu, event_button, event_time)


def show_main_window(menu):
    mainWindow.show_all()


def on_exit(menu):
    # exit_dialog.show()
    Gtk.main_quit()


handlers = {
    "on_exit": Gtk.main_quit,
    "status_popup_menu": on_status_popup_menu,
    "on_exit_item": on_exit,
    "on_show_item": show_main_window
}

builder = Gtk.Builder()
builder.add_from_file("ui/main.glade")
builder.add_from_file("ui/status.glade")
builder.add_from_file("ui/exit_dialog.glade")
builder.connect_signals(handlers)

mainWindow = builder.get_object("main_window")
tryIcon = builder.get_object("status")
exit_dialog = builder.get_object("exit_dialog")
# mainWindow.connect("delete-event", Gtk.main_quit)


if __name__ == "__main__":
    Gtk.main()
