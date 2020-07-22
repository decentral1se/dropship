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
loop = asyncio.get_event_loop()


class DropShip:
    """Drag it, drop it, ship it."""

    def __init__(self):
        self.GLADE_FILE = "dropship.glade"
        self.CSS_FILE = "dropship.css"

        self._running = loop.create_future()

        self.init_glade()
        self.init_css()
        self.init_drop_box()
        self.init_window()

    def init_glade(self):
        """Initialise the GUI from Glade file."""
        self.builder = gtk.Builder()
        self.builder.add_from_file(self.GLADE_FILE)
        self.builder.connect_signals(self)

    def init_css(self):
        """Initialise CSS injection."""
        self.screen = gdk.Screen.get_default()
        self.provider = gtk.CssProvider()
        self.provider.load_from_path(self.CSS_FILE)
        gtk.StyleContext.add_provider_for_screen(
            self.screen, self.provider, gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def init_window(self):
        """Initialise the GUI window."""
        self.main_window_id = "mainWindow"
        self.window = self.builder.get_object(self.main_window_id)
        self.window.connect("delete-event", self.on_quit)
        self.window.show()

    def init_drop_box(self):
        """Initialise the drag & drop box."""
        # Initiate the drag and drop area
        # https://python-gtk-3-tutorial.readthedocs.io/en/latest/drag_and_drop.html
        self.files_to_send = ""

        # todo check the target flags, https://lazka.github.io/pgi-docs/Gtk-3.0/flags.html#Gtk.TargetFlags
        self.enforce_target = gtk.TargetEntry.new("text/plain", gtk.TargetFlags(4), 129)

        self.drop_box_id = "dropBox"
        self.drop_box_label = "dropLabel"

        self.drop_box = self.builder.get_object(self.drop_box_id)
        self.drop_box.drag_dest_set(
            gtk.DestDefaults.ALL, [self.enforce_target], gdk.DragAction.COPY
        )
        self.drop_box.connect("drag-data-received", self.on_drop)
        self.drop_label = self.builder.get_object(self.drop_box_label)

    def on_drop(self, widget, drag_context, x, y, data, info, time):
        files = data.get_text().split()
        self.files_to_send = files
        if len(files) == 1:
            self.schedule(self.wormhole_send(self, files[0]))
            self.drop_label.set_text("Sending..")
        else:
            log.info("Multiple file sending coming soon ™")

    def on_quit(self, *args, **kwargs):
        """Quit the program."""
        self.window.close()

        # Note(decentral1se): this seems to be a hack but kinda works!?
        # enabled by https://github.com/jhenstridge/asyncio-glib/pull/7
        self._running.set_result(None)

    def schedule(self, function):
        """Schedule an task."""
        loop.call_soon_threadsafe(asyncio.ensure_future, function)

    async def wormhole_send(self, widget, fpath):
        """Run `wormhole send` on a local file path."""
        log.info(f"Pretending to start wormhole send {fpath}")
        await asyncio.sleep(2)
        log.info(f"Pretending to finish wormhole send {fpath}")


async def main():
    """The application entrypoint."""
    dropship = DropShip()
    await dropship._running


if __name__ == "__main__":
    try:
        # TODO(decentral1se): also handle Ctrl-C escape from terminal
        loop.run_until_complete(main())
    finally:
        loop.close()
