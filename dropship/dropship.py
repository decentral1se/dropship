from pathlib import Path
from subprocess import PIPE

from gi import require_version
from trio import open_process, run_process

from dropship import log

require_version("Gtk", "3.0")
require_version("Gdk", "3.0")

from gi.repository import Gdk as gdk
from gi.repository import Gtk as gtk


class DropShip:
    """Drag it, drop it, ship it."""

    def __init__(self, nursery):
        """Object initialisation."""
        self.CWD = Path(__file__).absolute().parent
        self.GLADE_FILE = f"{self.CWD}/ui/dropship.ui"
        self.CSS_FILE = f"{self.CWD}/ui/dropship.css"

        self.clipboard = gtk.Clipboard.get(gdk.SELECTION_CLIPBOARD)
        self.nursery = nursery

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
            self.nursery.start_soon(self.wormhole_send, fpath)
        else:
            log.info("Multiple file sending coming soon ™")

    def on_recv(self, entry):
        """Handler for receiving transfers."""
        self.nursery.start_soon(self.wormhole_recv, entry.get_text())

    def add_files(self, widget, event):
        """Handler for adding files with system interface"""
        response = self.file_chooser.run()
        if response == gtk.ResponseType.OK:
            fpath = self.file_chooser.get_filenames()[0]
            self.nursery.start_soon(self.wormhole_send, fpath)
        self.file_chooser.hide()

    async def wormhole_send(self, fpath):
        """Run `wormhole send` on a local file path."""
        command = ["wormhole", "send", fpath]
        process = await open_process(command, stderr=PIPE)

        self.drop_label.set_visible(False)
        self.drop_label.set_vexpand(False)

        self.drop_spinner.set_vexpand(True)
        self.drop_spinner.set_visible(True)
        self.drop_spinner.start()

        output = await process.stderr.receive_some()
        code = output.decode().split()[-1]

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
        await run_process(command, stderr=PIPE)
