from mbrat.commander import ConfigCommand
from mbrat.settings import MBRAT_POOLSD


class PoolCommand(ConfigCommand):
    name = "pool"
    description = "Manage public pools of Mandelbrot points."
    help = "public point pool manager"

    def __init__(self):
        super(PoolCommand, self).__init__()
        self.parser.set_defaults(command=self)

    def run_command(self, args):
        if args.rm:
            self.run_rm(args)
        else:
            self.run_ls(args)


# instantiate command
PoolCommand()
