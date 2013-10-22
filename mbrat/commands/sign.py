from os import path

from mbrat.commander import Command
from mbrat.configmgr import ConfigManager
from mbrat.functions import pyMFun

class SignCommand(Command):
    name = "sign"
    description = "Sign or validate a file using current profile privkey and a given target pubkey from the same pool. To stdout."
    help = "sign and validate plaintext"

    def __init__(self):
        super(SignCommand, self).__init__()
        self.group = self.parser.add_mutually_exclusive_group()
        self.group.add_argument( 
            "--sign", "-s", action='store_true',
            help="sign the INFILE" 
        )
        self.group.add_argument( 
            "--valid", "-v", action='store',
            help="validate the INFILE using given PUBKEY" 
        )
        self.parser.add_argument( "infile",
                                  help="the file to sign or validate" )

        self.parser.set_defaults(command=self)

        # init spi for this command 
        self.spi = None

        # instantiate a ConfigManager
        self.cfgmgr = ConfigManager()
        self.config = self.cfgmgr.secmgr['profile']


    def run_command(self, args):

        if not path.exists(args.infile):
            exit("==> ERROR: infile not found:\n  -> {}".format(args.infile))
        inf = open(args.infile, 'r')
        plaintext = inf.read()
        inf.close()

        # set arguments here for class-wide parameters
        args.plaintext = plaintext

        if args.sign:
            self.run_sign(args)
        elif args.valid:
            self.run_valid(args)


    def run_sign(self, args):

        from mbrat.spi.sign import SignSPI
        self.spi = SignSPI(pyMFun)

        privkey_cfg = self.cfgmgr.secmgr['privkey']
        poolkey_cfg = self.cfgmgr.secmgr['poolkey']

        print "{0}: signing '{1}' using ".format(
            self.config.get('name'), args.infile ), 
        print "private key '{0}' and poolkey '{1}".format(
            privkey_cfg.get('name'), poolkey_cfg.get('name') )

        sighash = self.spi.run(args)

        print sighash

    
    def run_valid(self, args):

        from mbrat.spi.sign import ValidateSPI
        self.spi = ValidateSPI(pyMFun)

        print "Validating '{0}'\n  -> source pubkey {1} ...".format(
            args.infile, args.valid)

        isvalid = self.spi.run(args)


# instantiate command
SignCommand()
