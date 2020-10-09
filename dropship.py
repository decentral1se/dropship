"""Magic-Wormhole bundled up inside a PyGtk GUI."""

import logging
import os
from signal import SIGINT
from subprocess import PIPE

import gi
import trio
import trio_gtk

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")

from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import Gtk

from ui_templates import pendingTransmissions

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

log = logging.getLogger("dropship")


class DropShip:
    """Drag it, drop it, ship it."""

    def __init__(self, nursery):
        """Object initialisation."""
        self.GLADE_FILE = "dropship.glade"
        self.CSS_FILE = "dropship.css"
        self.DOWNLOAD_DIR = os.path.expanduser("~")

        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.nursery = nursery

        self.init_glade()
        self.init_css()
        self.init_ui_elements()
        self.init_window()

    def init_glade(self):
        """Initialise the GUI from Glade file."""
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.GLADE_FILE)
        self.builder.connect_signals(self)

    def init_css(self):
        """Initialise CSS injection."""
        self.screen = Gdk.Screen.get_default()
        self.provider = Gtk.CssProvider()
        self.provider.load_from_path(self.CSS_FILE)
        Gtk.StyleContext.add_provider_for_screen(
            self.screen, self.provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def init_window(self):
        """Initialise the Main GUI window."""
        self.main_window_id = "mainWindow"
        self.window = self.builder.get_object(self.main_window_id)
        self.window.connect("delete-event", Gtk.main_quit)
        self.window.show()

    def init_ui_elements(self):
        """Initialize the UI elements."""

        # Send UI
        # Drag & Drop Box
        self.files_to_send = ""
        self.enforce_target = Gtk.TargetEntry.new(
            "text/uri-list", Gtk.TargetFlags(4), 129
        )

        self.drop_box = self.builder.get_object("dropBox")
        self.drop_box.drag_dest_set(
            Gtk.DestDefaults.ALL, [self.enforce_target], Gdk.DragAction.COPY
        )
        self.drop_box.connect("drag-data-received", self.on_drop)
        self.drop_label = self.builder.get_object("dropLabel")
        self.drop_spinner = self.builder.get_object("dropSpinner")

        # File chooser
        self.file_chooser = self.builder.get_object("filePicker")
        self.file_chooser.add_buttons(
            "Cancel", Gtk.ResponseType.CANCEL, "Add", Gtk.ResponseType.OK
        )

        # Receive UI
        # Code entry box
        self.recv_box = self.builder.get_object("receiveBoxCodeEntry")
        self.recv_box.connect("activate", self.on_recv)

        # Pending Transmissions UI
        self.pending_box = self.builder.get_object("pendingBox")
        self.transfer_code = ''


    def on_drop(self, widget, drag_context, x, y, data, info, time):
        """Handler for file dropping."""
        files = data.get_uris()
        self.files_to_send = files
        if len(files) == 1:
            fpath = files[0].replace("file://", "")
            # TODO Luke can u make a callback that spawns pendingTransmissions after we got a code?
            self.nursery.start_soon(self.wormhole_send, fpath)

            # TODO Roel/Luke, move this somewhere logical in its own function?
            status = pendingTransmissions(self, fpath.split('/')[-1], self.transfer_code)
            self.pending_box.add(status)

        else:
            log.info("Multiple file sending coming soon ™")

    def on_recv(self, entry):
        """Handler for receiving transfers."""
        self.nursery.start_soon(self.wormhole_recv, entry.get_text())

    def add_files(self, widget, event):
        """Handler for adding files with system interface"""
        response = self.file_chooser.run()
        if response == Gtk.ResponseType.OK:
            fpath = self.file_chooser.get_filenames()[0]
            self.nursery.start_soon(self.wormhole_send, fpath)
        self.file_chooser.hide()

    async def wormhole_send(self, fpath):
        """Run `wormhole send` on a local file path."""
        command = ["wormhole", "send", fpath]
        process = await trio.open_process(command, stderr=PIPE)

        self.drop_label.set_visible(False)
        self.drop_label.set_vexpand(False)

        self.drop_spinner.set_vexpand(True)
        self.drop_spinner.set_visible(True)
        self.drop_spinner.start()

        output = await process.stderr.receive_some()
        code = output.decode().split()[-1]
        self.transfer_code = code  

        self.drop_label.set_text(code)
        self.drop_label.set_visible(True)
        self.drop_label.set_selectable(True)

        self.drop_spinner.stop()
        self.drop_spinner.set_vexpand(False)
        self.drop_spinner.set_visible(False)

        await process.wait()

    async def wormhole_recv(self, code):
        """Run `wormhole receive` with a pending transfer code."""
        command = ["wormhole", "receive", "--accept-file", code]
        await trio.run_process(command, stderr=PIPE)

async def main():
    """Trio main entrypoint."""
    async with trio.open_nursery() as nursery:
        DropShip(nursery)
        await trio.sleep_forever()


trio_gtk.run(main)
