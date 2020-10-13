from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gdk, GLib, Gtk

from dropship import log
from dropship.constant import DEFAULT_DROP_LABEL, UI_DIR


@Gtk.Template.from_file(f"{UI_DIR}/pendingTransferRow.ui")
class PendingTransferRow(Gtk.ListBoxRow):
    __gtype_name__ = "pendingTransferRow"

    fileNameLabel = Gtk.Template.Child()
    fileNameMetadata = Gtk.Template.Child()
    transferCodeButton = Gtk.Template.Child()
    cancelTransfer = Gtk.Template.Child()
    pendingTransferRow = Gtk.Template.Child()

    def __init__(self, transfer, parent, *args, **kwargs):
        Gtk.ListBoxRow.__init__(self, *args, **kwargs)
        self.transfer = transfer
        self.parent = parent
        self.fileNameLabel.set_text(self.transfer.fname)
        self.fileNameMetadata.set_text(self.transfer.size)
        self.transferCodeButton.set_label(self.transfer.code)

    @property
    def code(self):
        """Retrieve code of underyling transfer."""
        return self.transfer.code

    @Gtk.Template.Callback("copy_transfer_code")
    def copy_transfer_code(self, widget):
        """Copy transfer code to clipboard."""
        code = widget.get_label()
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(code, -1)  # -1 is auto-size

    @Gtk.Template.Callback("cancel_transfer")
    def cancel_transfer(self, widget):
        """Callback entrypoint for transfer cancellation."""
        self.cancel()

    def cancel(self):
        """Internal programmatic API for transfer cancellation."""
        self.transfer.cancel()
        self.pendingTransferRow.destroy()
        self.parent.drop_label.set_text(DEFAULT_DROP_LABEL)
        self.parent.drop_label.set_selectable(False)
        log.info(
            f"PendingTransferRow: successfully cancelled transfer ({self.transfer.code})"
        )
