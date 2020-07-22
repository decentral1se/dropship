import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")

from gi.repository import Gdk, GLib, Gtk


class Main:
    def __init__(self):

        # Connect to the Glade file
        self.builder = Gtk.Builder()
        self.builder.add_from_file("dropship.glade")
        self.builder.connect_signals(self)

        # Connect to the Stylesheet
        screen = Gdk.Screen.get_default()
        provider = Gtk.CssProvider()
        provider.load_from_path("./dropship.css")
        Gtk.StyleContext.add_provider_for_screen(
            screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        window = self.builder.get_object("mainWindow")
        window.connect("delete-event", Gtk.main_quit)
        window.show()

        # self.stack = self.builder.get_object("sendReceiveStack")

        # Initiate the drag and drop area
        # https://python-gtk-3-tutorial.readthedocs.io/en/latest/drag_and_drop.html
        self.files_to_send = ""

        # todo check the target flags, https://lazka.github.io/pgi-docs/Gtk-3.0/flags.html#Gtk.TargetFlags
        enforce_target = Gtk.TargetEntry.new("text/plain", Gtk.TargetFlags(4), 129)

        self.dropBox = self.builder.get_object("dropBox")
        self.dropBox.drag_dest_set(
            Gtk.DestDefaults.ALL, [enforce_target], Gdk.DragAction.COPY
        )
        self.dropBox.connect("drag-data-received", self.onDrop)
        self.dropLabel = self.builder.get_object("dropLabel")

    def onDrop(self, widget, drag_context, x, y, data, info, time):
        print(drag_context, x, y, data, info, time)
        files = data.get_text().split()

        if len(files) == 1:
            print(files)
            self.dropLabel.set_text("Sending..")
        elif len(files) > 1:
            print("multiple files!")
            print(files)
            self.dropLabel.set_text("\n".join(files))

        self.files_to_send = files


if __name__ == "__main__":
    Main()
    Gtk.main()
