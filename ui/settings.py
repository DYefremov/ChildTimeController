import pwd
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


def get_users_list():
    users_list = []
    for p in pwd.getpwall():
        if p[5].startswith("/home/") and p[6] != "/bin/false":
            users_list.append(p[0])
    return users_list


class SettingsDialog:

    _builder = Gtk.Builder()
    _builder.add_from_file("ui/main.glade")
    _mainWindow = _builder.get_object("main_window")

    def __init__(self):
        self._init_users_box()

    def show_settings_dialog(self):
        self._mainWindow.show_all()

    def hide_settings_dialog(self):
        self._mainWindow.destroy()

    def _init_users_box(self):
        users = get_users_list()
        self.users_box = self._builder.get_object("usersBox")
        self.list = Gtk.ListStore(str)

        for u in users:
            self.list.append([u])

        self.users_box.set_model(self.list)
        self.users_box.set_active(0)
        cell = Gtk.CellRendererText()
        self.users_box.pack_start(cell, True)
        self.users_box.add_attribute(cell, "text", 0)