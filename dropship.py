"""Magic-Wormhole bundled up inside a PyGtk GUI."""

import logging
import os
from signal import SIGINT, SIGTERM
from subprocess import PIPE, Popen, TimeoutExpired

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")

from gi.repository import Gdk as gdk
from gi.repository import GLib as glib
from gi.repository import Gtk as gtk

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

log = logging.getLogger("dropship")

AUTO_CLIP_COPY_SIZE = -1


class PendingTransfer:
    """A wormhole send waiting for a wormhole receive."""

    def __init__(self, code, fpath, process):
        """Object initialisation."""
        self.fpath = fpath
        self.code = code
        self.process = process


class DropShip:
    """Drag it, drop it, ship it."""

    def __init__(self):
        """Object initialisation."""
        self.GLADE_FILE = "dropship.glade"
        self.CSS_FILE = "dropship.css"
        self.DOWNLOAD_DIR = os.path.expanduser("~")

        self.clipboard = gtk.Clipboard.get(gdk.SELECTION_CLIPBOARD)

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
        self.window.connect("delete-event", gtk.main_quit)
        self.window.show()

    def init_ui_elements(self):
        """Initialize the UI elements."""

        # TODO (rra) find out how to use composite templates
        # https://github.com/sebp/PyGObject-Tutorial/issues/149

        # Send UI
        # Drag & Drop Box
        self.files_to_send = ""
        self.enforce_target = gtk.TargetEntry.new(
            "text/uri-list", gtk.TargetFlags(4), 129
        )

        self.drop_box = self.builder.get_object("dropBox")
        self.drop_box.drag_dest_set(
            gtk.DestDefaults.ALL, [self.enforce_target], gdk.DragAction.COPY
        )
        self.drop_box.connect("drag-data-received", self.on_drop)
        self.drop_label = self.builder.get_object("dropLabel")
        self.drop_spinner = self.builder.get_object("dropSpinner")

        # File chooser
        self.file_chooser = self.builder.get_object("filePicker")
        self.file_chooser.add_buttons(
            "Cancel", gtk.ResponseType.CANCEL, "Add", gtk.ResponseType.OK
        )

        # Receive UI
        # Code entry box
        self.recv_box = self.builder.get_object("receiveBoxCodeEntry")
        self.recv_box.connect("activate", self.on_recv)

    def on_drop(self, widget, drag_context, x, y, data, info, time):
        """Handler for file dropping."""
        files = data.get_uris()
        self.files_to_send = files
        if len(files) == 1:
            fpath = files[0].replace("file://", "")
            self.wormhole_send(self, fpath)
            self.drop_label.set_text("Sending..")
            self.drop_spinner.start()

        else:
            log.info("Multiple file sending coming soon ™")

    def add_files(self, widget, event):
        """Handler for adding files with system interface"""
        response = self.file_chooser.run()
        if response == gtk.ResponseType.OK:
            self.wormhole_send(self, self.file_chooser.get_filenames()[0])
        elif response == gtk.ResponseType.CANCEL:
            # TODO(roel) something isn't right here.. maybe we need to initialize it every time we run it.
            print("Cancel clicked")
        self.file_chooser.destroy()

    def read_wormhole_send_code(self, process):
        """Read wormhole send code from command-line output."""
        process.stderr.readline()  # NOTE(decentral1se): skip first line
        code_line = process.stderr.readline()
        return code_line.split()[-1].decode("utf-8")

    def on_recv(self, entry):
        """Handler for receiving transfers."""
        code = entry.get_text()
        self.wormhole_recv(self, code)

    def wormhole_send(self, widget, fpath):
        """Run `wormhole send` on a local file path."""
        command = ["wormhole", "send", fpath]
        process = Popen(command, stderr=PIPE)
        code = self.read_wormhole_send_code(process)

        self.drop_label.set_selectable(True)
        self.drop_label.set_text(code)
        self.drop_spinner.stop()

        self.clipboard.set_text(code, AUTO_CLIP_COPY_SIZE)

        self._pending.append(PendingTransfer(code, fpath, process))

    def wormhole_recv(self, widget, code):
        """Run `wormhole receive` with a pending transfer code."""
        command = ["wormhole", "receive", "--accept-file", code]
        process = Popen(command, stderr=PIPE)
        process.communicate()


if __name__ == "__main__":
    DropShip()
    gtk.main()
