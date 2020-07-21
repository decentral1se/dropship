
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk

class Main:
    def __init__(self):
        self.timer = None
        self.event = None
        self.timer_running = False
        
        # Connect to the Glade file
        self.builder = Gtk.Builder()
        self.builder.add_from_file('dropship.glade')
        self.builder.connect_signals(self)

        # Connect to the Stylesheet
        screen = Gdk.Screen.get_default()
        provider = Gtk.CssProvider()
        provider.load_from_path("./dropship.css")
        Gtk.StyleContext.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
      
        window = self.builder.get_object("mainWindow")
        window.connect('delete-event', Gtk.main_quit)
        window.show()

        #self.stack = self.builder.get_object("mainStack")

if __name__ == '__main__':
    main = Main()
    Gtk.main()
