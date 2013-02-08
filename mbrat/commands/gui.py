from gi.repository import Gtk
from mbrat.commander import Command
from mbrat.mbrat_gui.mbratgui import mbratgui

class GUICommand(Command):
    name = "gui"
    description = "Launch the GUI version of MBrat."
    help = "launch the mbrat GUI"

    def __init__(self):
        super(GUICommand, self).__init__()
        self.parser.set_defaults(command=self)

    def run_command(self, args):
        mbratgui_instance = mbratgui()
        Gtk.main()

# instantiate command
GUICommand()
