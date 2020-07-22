"""Magic-Wormhole bundled up inside a PyGtk GUI."""

import asyncio
import logging
import os

import asyncio_glib
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")

from gi.repository import Gdk as gdk
from gi.repository import GLib as glib
from gi.repository import Gtk as gtk

asyncio.set_event_loop_policy(asyncio_glib.GLibEventLoopPolicy())
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

log = logging.getLogger("dropship")


class DropShip:
    """Drag it, drop it, ship it."""

    def __init__(self):
        self.GLADE_FILE = "dropship.glade"
        self.CSS_FILE = "dropship.css"

        # Initiate the drag and drop area
        # https://python-gtk-3-tutorial.readthedocs.io/en/latest/drag_and_drop.html
        self.files_to_send = ""

        # todo check the target flags, https://lazka.github.io/pgi-docs/Gtk-3.0/flags.html#Gtk.TargetFlags
        self.enforce_target = gtk.TargetEntry.new("text/plain", gtk.TargetFlags(4), 129)

        self.main_window_id = "mainWindow"

        self.drop_box_id = "dropBox"
        self.drop_box_label = "dropLabel"

        self.init_glade()
        self.init_css()
        self.init_drop_box()

    def init_glade(self):
        """Initialise the GUI from Glade file."""
        self.builder = gtk.Builder()
        self.builder.add_from_file(self.GLADE_FILE)
        self.builder.connect_signals(self)

    def init_css(self):
        """Initialise CSS injection."""
        screen = gdk.Screen.get_default()
        provider = gtk.CssProvider()
        provider.load_from_path(self.CSS_FILE)
        gtk.StyleContext.add_provider_for_screen(
            screen, provider, gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    async def init_window(self):
        """Initialise the GUI window."""
        window = self.builder.get_object(self.main_window_id)
        window.connect("delete-event", gtk.main_quit)
        window.show()

    def init_drop_box(self):
        """Initialise the drag & drop box."""
        self.dropBox = self.builder.get_object(self.drop_box_id)
        self.dropBox.drag_dest_set(
            gtk.DestDefaults.ALL, [self.enforce_target], gdk.DragAction.COPY
        )
        self.dropBox.connect("drag-data-received", self.on_drop)
        self.dropLabel = self.builder.get_object(self.drop_box_label)

    def on_drop(self, widget, drag_context, x, y, data, info, time):
        files = data.get_text().split()
        if len(files) == 1:
            # TODO: wormhole send that file
            self.dropLabel.set_text("Sending..")
        self.files_to_send = files


async def main():
    """The application entrypoint."""
    dropship = DropShip()
    await dropship.init_window()


if __name__ == "__main__":
    asyncio.run(main())
