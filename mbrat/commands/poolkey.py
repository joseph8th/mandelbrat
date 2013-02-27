from os import path

from mbrat.commander import ConfigCommand


class PoolKeyCommand(ConfigCommand):
    name = "poolkey"
    description = "Manage public key-points (poolkey) from the current public pool."
    help = "public poolkey manager"

    def __init__(self):
        super(PoolKeyCommand, self).__init__()
        self.group.add_argument( "--pkrand", action='store_true',
                                 help="pick a random public key-point from current pool" )
        self.parser.set_defaults(command=self)


    def run_command(self, args):
        if args.rm:
            self.run_rm(args)
        elif args.pkrand:
            self.run_pkrand(args)
        else:
            self.run_ls(args)


# instantiate command
PoolKeyCommand()
