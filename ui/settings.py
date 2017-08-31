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
    def __init__(self):
        self._init_ui()
        self._init_users_box()
        self.response = self._main_dialog.run()
        if self.response == Gtk.ResponseType.OK:
            print("The Apply was clicked")
        else:
            print("The Cancel was clicked")
            self._main_dialog.destroy()

    def hide_settings_dialog(self):
        self._main_dialog.hide()

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

    def _init_ui(self):
        self._builder = Gtk.Builder()
        self._builder.add_from_file("ui/main.glade")
        self._main_dialog = self._builder.get_object("main_dialog")
        # init ui elements
        self._cancel_button = self._builder.get_object("cancel_button")
        self._apply_button = self._builder.get_object("apply_button")
        self._exit_menu_item = self._builder.get_object("exit_menu_item")
        self._about_menu_item = self._builder.get_object("about_menu_item")
        self._session_duration = self._builder.get_object("session_duration")
        self._pause_between_sessions = self._builder.get_object("pause_between_sessions")

        handlers = {
            "on_about_menu_item_activate": on_about_dialog
        }

        self._builder.connect_signals(handlers)


if __name__ == "__main__":
    pass
