import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk

@Gtk.Template.from_file('pendingTransmissions.ui')
class pendingTransmissions(Gtk.Box):
    __gtype_name__ = 'PendingTransmission'

    fileNameLabel           = Gtk.Template.Child()
    fileNameMetadata        = Gtk.Template.Child()
    transmissionCodeButton  = Gtk.Template.Child()
    cancelTransmission      = Gtk.Template.Child()

    def __init__(self, parent, fileName, transferCode):
        super(Gtk.Box, self).__init__()
        #Gtk.Frame.__init__(self)    
        # This must occur *after* you initialize your base
        self.init_template()
        #TODO (Roel)
        self.fileNameLabel.set_ellipsize(2)  
        self.fileNameLabel.set_text(fileName)

        self.transmissionCodeButton.set_label(transferCode)

    @Gtk.Template.Callback()
    def transfer_button_click(self,widget):
        '''
        what to do when we press the button:
        copy the code again to clipboard
        '''
        print('click')

    @Gtk.Template.Callback()
    def cancel_transfer(self,widget):
        '''
        cancel the transfer
        destroy thread
        remove the object from the list
        '''
        print('poof!')