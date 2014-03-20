import os
from os import path
from shutil import rmtree
#from mpmath import mp, mpc, nstr
#from mpmath import mpmathify as mpify

from mbrat.commander import ConfigCommand
from mbrat.lib.mscreen import PyMScreen
from mbrat.util import arglist_parse_to_dict
from mbrat.mutil import mandelfun
from mbrat.mutil import MultiLibMPC as mlmpc


class PrivKeyCommand(ConfigCommand):
    name = "privkey"
    description = "Private key manager."
    help = "private key manager"

    def __init__(self):
        super(PrivKeyCommand, self).__init__()
        self.privpool_group = self.parser.add_argument_group("subcommand group", "subcommand-specific options")

        self.privpool_group.add_argument( "--vipool", action='store_true',
                                 help="view info about private pool for current privkey" )
        self.privpool_group.add_argument( "--setpool", nargs='*',
                                 help="set private pool config properties" )
        self.privpool_group.add_argument( "--pkrand", action='store_true',
                                 help="pick a random private key-point from private pool" )

        self.parser.set_defaults(command=self)


    def run_command(self, args):
        if args.rm:
            self.run_rm(args)
        elif args.vipool:
            self.run_vipool(args)
        elif args.setpool:
            self.run_setpool(args)
        elif args.pkrand:
            self.run_pkrand(args)
        else:
            self.run_ls(args)


    def run_vipool(self, args):
        self.config.set_section_to('pool')
        self.name = self.config.get('name')
        self.run_vi(args)


    def run_setpool(self, args):
        self.config.set_section_to('pool')
        self.name = self.config.get('name')
        args.set = args.setpool
        self.run_set(args)

        

# instantiate command
PrivKeyCommand()
