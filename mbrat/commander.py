import os
from sys import modules
from os.path import join, splitext
from mbrat.argparser import subparsers
from mbrat import commands

class Command(object):
    """
    Parent class for commands.
    """
    name = None
    description = ""
    help = ""

    def __init__(self):
        self.parser = subparsers.add_parser(name = self.name,
                                            description = self.description, 
                                            help = self.help)
    def run(self, args):
        """
        Sends parsed arguments to given subcommand's run_command() method.
        """
        self.run_command(args)


### load subcommands funcs ###

def _load_command(name):
    command = 'mbrat.commands.%s' % name
    if command in modules:
        return
    try:
        __import__(command)
    except ImportError:
        print "ImportError: unable to import %s" % command
#        pass

def get_cmd_list():
    """
    Assumes /commands/*.py are commands if '__' is not in filename.
    """
    return [fname for fname, fext in map( splitext, 
                                          os.listdir(join(os.getcwd(), 'mbrat/commands')) )
            if fext == '.py' and '__' not in fname]


def load_commands():
    """
    Load all commands.
    """
    cmd_l = get_cmd_list()
    for name in cmd_l:
        _load_command(name)
