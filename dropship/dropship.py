from os.path import basename
from pathlib import Path
from subprocess import PIPE

from gi import require_version
from trio import open_process, run_process

from dropship import log

require_version("Gtk", "3.0")
require_version("Gdk", "3.0")

from gi.repository import Gdk, GLib, Gtk

from dropship.ui_templates import pendingTransferRow

CWD = Path(__file__).absolute().parent


class DropShip:
    """Drag it, drop it, ship it."""

    def __init__(self, nursery):
        """Object initialisation."""
        self.GLADE_FILE = f"{CWD}/ui/dropship.ui"
        self.CSS_FILE = f"{CWD}/ui/dropship.css"

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

        # Pending Transfers UI
        self.pending_transfers_list = self.builder.get_object(
            "pendingTransfersList"
        )
        self.transfer_code = ""

    def on_drop(self, widget, drag_context, x, y, data, info, time):
        """Handler for file dropping."""
        files = data.get_uris()
        self.files_to_send = files
        if len(files) == 1:
            fpath = files[0].replace("file://", "")
            fname = basename(fpath)
            # TODO Luke can u make a callback that spawns pendingTransmissions after we got a code?
            self.nursery.start_soon(self.wormhole_send, fpath)

            # TODO Roel/Luke, move this somewhere logical in its own function?
            status = pendingTransferRow(self, fname, self.transfer_code)

            # TODO Roel, find out how to add to a listbox
            self.pending_transfers_list.insert(
                status, -1
            )  # -1 is add at bottom

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

    def _send_spinner_on(self):
        """Turn spinner on for sending interaction."""
        self.drop_label.set_visible(False)
        self.drop_label.set_vexpand(False)
        self.drop_spinner.set_vexpand(True)
        self.drop_spinner.set_visible(True)
        self.drop_spinner.start()

    def _send_spinner_off(self):
        """Turn spinner off for sending interaction."""
        self.drop_label.set_text(self.transfer_code)
        self.drop_label.set_visible(True)
        self.drop_label.set_selectable(True)
        self.drop_spinner.stop()
        self.drop_spinner.set_vexpand(False)
        self.drop_spinner.set_visible(False)

    async def wormhole_send(self, fpath):
        """Run `wormhole send` on a local file path."""
        self._send_spinner_on()
        process = await open_process(["wormhole", "send", fpath], stderr=PIPE)
        output = await process.stderr.receive_some()
        self.transfer_code = output.decode().split()[-1]
        self.clipboard.set_text(self.transfer_code, -1)
        self._send_spinner_off()
        await process.wait()

    async def wormhole_recv(self, code):
        """Run `wormhole receive` with a pending transfer code."""
        command = ["wormhole", "receive", "--accept-file", code]
        await run_process(command, stderr=PIPE)
