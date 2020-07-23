"""Magic-Wormhole bundled up inside a PyGtk GUI."""

import asyncio
import logging
import os
import subprocess
from pathlib import Path
from signal import SIGINT, SIGTERM

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

AUTO_CLIP_COPY_SIZE = -1


class PendingTransfer:
    """A wormhole send waiting for a wormhole receive."""

    def __init__(self, code):
        """Object initialisation."""
        self.code = code


class DropShip:
    """Drag it, drop it, ship it."""

    def __init__(self):
        """Object initialisation."""
        self.GLADE_FILE = "dropship.glade"
        self.CSS_FILE = "dropship.css"
        self.DOWNLOAD_DIR = os.path.expanduser("~")

        self.clipboard = gtk.Clipboard.get(gdk.SELECTION_CLIPBOARD)

        self._running = loop.create_future()
        self._pending = []

        self.init_glade()
        self.init_css()
        self.init_ui_elements()
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
        """Initialise the Main GUI window."""
        self.main_window_id = "mainWindow"
        self.window = self.builder.get_object(self.main_window_id)
        self.window.connect("delete-event", self.on_quit)
        self.window.show()

    def init_ui_elements(self):
        """Initialize the UI elements."""

        # Send UI
        # Drag & Drop Box
        self.files_to_send = ""
        self.enforce_target = gtk.TargetEntry.new("text/uri-list", gtk.TargetFlags(4), 129)

        self.drop_box = self.builder.get_object('dropBox')
        self.drop_box.drag_dest_set(
            gtk.DestDefaults.ALL, [self.enforce_target], gdk.DragAction.COPY
        )
        self.drop_box.connect("drag-data-received", self.on_drop)
        self.drop_label = self.builder.get_object('dropLabel')

        # File chooser
        self.file_chooser = self.builder.get_object('filePicker')
        self.file_chooser.add_buttons(
            'Cancel', gtk.ResponseType.CANCEL, "Add", gtk.ResponseType.OK
        )
 
        # Receive UI
        # Code entry box
        self.recv_box = self.builder.get_object('receiveBoxCodeEntry')
        self.recv_box.connect("activate", self.on_recv)


    def on_drop(self, widget, drag_context, x, y, data, info, time):
        """Handler for file dropping."""
        files = data.get_uris()
        self.files_to_send = files
        if len(files) == 1:
            fpath = Path(files[0].replace("file://", ""))
            self.schedule(self.wormhole_send(self, fpath))
            self.drop_label.set_text("Sending..")
        else:
            log.info("Multiple file sending coming soon ™")

    def add_files(self,widget, event):
        """Handler for adding files with system interface"""
        response = self.file_chooser.run()
        if response == gtk.ResponseType.OK:
            self.schedule(self.wormhole_send(self, self.file_chooser.get_filenames()[0]))
        elif response == gtk.ResponseType.CANCEL:
            #TODO(roel) something isn't right here.. maybe we need to initialize it every time we run it.
            print("Cancel clicked")
        self.file_chooser.destroy()

    def on_recv(self, entry):
        """Handler for receiving transfers."""
        code = entry.get_text()
        self.schedule(self.wormhole_recv(self, code))

    def on_quit(self, *args, **kwargs):
        """Quit the program."""
        self.window.close()
        self._running.set_result(None)

    def schedule(self, function):
        """Schedule a task on the event loop."""
        loop.call_soon_threadsafe(asyncio.ensure_future, function)

    async def read_lines(self, stream, pattern):
        """Read stdout from a command and match lines."""
        # TODO(decentral1se): if pattern doesnt match, trapped forever
        while True:
            line = await stream.readline()
            decoded = line.decode("utf-8").strip()
            if pattern in decoded:
                return decoded

    async def wormhole_send(self, widget, fpath):
        """Run `wormhole send` on a local file path."""
        process = await asyncio.create_subprocess_exec(
            "wormhole",
            "send",
            "--hide-progress",
            fpath,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        line = await self.read_lines(process.stderr, "wormhole receive")
        code = line.split()[-1]

        self.drop_label.set_selectable(True)
        self.drop_label.set_text(code)

        self.clipboard.set_text(code, AUTO_CLIP_COPY_SIZE)

        self._pending.append(PendingTransfer(code))

        await process.wait()

    async def wormhole_recv(self, widget, code):
        """Run `wormhole receive` with a pending transfer code."""
        process = await asyncio.create_subprocess_exec(
            "wormhole",
            "receive",
            "--accept-file",
            "--hide-progress",
            code,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.wait()


async def main():
    """The application entrypoint."""
    try:
        dropship = DropShip()
        await dropship._running
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    try:
        main_task = asyncio.ensure_future(main())
        loop.add_signal_handler(SIGINT, main_task.cancel)
        loop.add_signal_handler(SIGTERM, main_task.cancel)
        loop.run_until_complete(main_task)
    finally:
        loop.close()
