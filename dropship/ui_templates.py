from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gdk, GLib, Gtk

CWD = Path(__file__).absolute().parent


@Gtk.Template.from_file(f"{CWD}/ui/pendingTransferRow.ui")
class PendingTransferRow(Gtk.ListBoxRow):
    # Note(decentral1se): must match ui/pendingTransferRow.ui name
    __gtype_name__ = "pendingTransferRow"

    fileNameLabel = Gtk.Template.Child()
    fileNameMetadata = Gtk.Template.Child()
    transferCodeButton = Gtk.Template.Child()
    cancelTransfer = Gtk.Template.Child()

    def __init__(self, fileName, transferCode):
        super(PendingTransferRow, self).__init__()
        self.fileNameLabel.set_text(fileName)
        self.transferCodeButton.set_label(transferCode)

    @Gtk.Template.Callback()
    def copy_transfer_code(self, widget):
        """
        what to do when we press the button:
        copy the code again to clipboard
        """
        print("click")
        code = widget.get_label()

        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(code, -1)  # -1 is auto-size

    @Gtk.Template.Callback()
    def cancel_transfer(self, widget):
        """
        cancel the transfer
        destroy thread
        remove the object from the list
        """
        print("poof!")
