import png
from os import path
from gi.repository import Gtk
from mbrat.settings import MBRAT_GUID_GLADEF, MBRAT_TMP_IMGF, cmap_fun
from mbrat.mscreen import PyMScreen

class Arguments(object):
    pass


class mbratgui:
    """
    The main GUI class that does all the gooey stuff for mbrat engine.
    """
    def __init__(self):
        handler_d = {
            "on_genMSetButton_pressed": self.on_genMSetButton_pressed,
            "on_MainWindow_delete_event": self.on_MainWindow_delete_event,
            }

        self.builder = Gtk.Builder()
        self.builder.add_from_file( MBRAT_GUID_GLADEF )
        self.builder.connect_signals( handler_d )

        self.window = self.builder.get_object( "MainWindow" )

        self.image = self.builder.get_object("mscreenImage")

        self.consoleView = self.builder.get_object("MSetInfoTextview")
        self.consoleBuffer = self.consoleView.get_buffer()
        self.consoleView.set_buffer(self.consoleBuffer)
        self.consoleBuffer.set_text("")

        self.window.show_all()

    # return the values in the gui entry fields
    def _parse_parameterGrid_values(self):
        self.args = Arguments()
        self.args.iters = int(self.builder.get_object("maxiterEntry").get_text())
        self.args.ppu = int(self.builder.get_object("ppuEntry").get_text())
        xLo = self.builder.get_object("xLoEntry").get_text()    
        yLo = self.builder.get_object("yLoEntry").get_text()    
        xHi = self.builder.get_object("xHiEntry").get_text()    
        yHi = self.builder.get_object("yHiEntry").get_text()
        self.args.lims = { 'low':complex( float(xLo), float(yLo) ), 
                      'high':complex( float(xHi), float(yHi) ) }
        c = self.builder.get_object("cmapComboboxtext").get_active_text()
        if "Grayscale" in c:
            self.args.cmap = 'grey'
        else:
            self.args.cmap = 'bw'

    # if 'Generate Mandelbrot Set' button is pressed
    def on_genMSetButton_pressed(self, button):
        #        mset_info = ms.get_info()
        self._parse_parameterGrid_values()
        self.mscreen = PyMScreen(self.args)
        self.consoleBuffer.insert_at_cursor( self.mscreen.get_info() )
        self.mscreen.gen_mscreen()
        self.mscreen.gen_mset()

        img = self.mscreen.get_img()

        f = open(MBRAT_TMP_IMGF, 'wb')
        w = png.Writer(len(img[0]), len(img), greyscale=True, bitdepth=8)
        w.write(f, img)
        f.close()

        self.image.set_from_file(MBRAT_TMP_IMGF)

    # if the window is closed
    def on_MainWindow_delete_event(self, *args):
        Gtk.main_quit(args)
