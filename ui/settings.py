import pwd

from gi.repository import Gtk


def get_users_list():
    users_list = []
    for p in pwd.getpwall():
        if p[5].startswith("/home/") and p[6] != "/bin/false":
            users_list.append(p[0])
    return users_list


def on_about_dialog(item):
    builder = Gtk.Builder()
    builder.add_from_file("ui/about_dialog.glade")
    dialog = builder.get_object("about_dialog")
    dialog.run()
    dialog.hide()


class SettingsDialog:
    _builder = Gtk.Builder()
    _builder.add_from_file("ui/main.glade")
    _mainWindow = _builder.get_object("main_window")
    # init ui elements
    _cancel_button = _builder.get_object("cancel_button")
    _apply_button = _builder.get_object("apply_button")
    _exit_menu_item = _builder.get_object("exit_menu_item")
    _about_menu_item = _builder.get_object("about_menu_item")
    _session_duration = _builder.get_object("session_duration")
    _pause_between_sessions = _builder.get_object("pause_between_sessions")

    handlers = {
        "on_about_menu_item_activate": on_about_dialog
    }

    _builder.connect_signals(handlers)

    def __init__(self):
        self._init_users_box()

    def show_settings_dialog(self):
        self._mainWindow.show()

    def hide_settings_dialog(self):
        self._mainWindow.hide()

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


if __name__ == "__main__":
    pass
