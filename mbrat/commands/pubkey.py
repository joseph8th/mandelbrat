from os import path
from mbrat.commander import ConfigCommand


class PubKeyCommand(ConfigCommand):
    name = "pubkey"
    description = "Public key manager."
    help = "public key manager"

    def __init__(self):
        super(PubKeyCommand, self).__init__()
        self.parser.set_defaults(command=self)

    def run_command(self, args):
        if args.rm:
            self.run_rm(args, cfglink=True)
        else:
            self.run_ls(args)


# instantiate command
PubKeyCommand()
