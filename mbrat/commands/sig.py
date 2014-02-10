from os import path
import gmpy2
from gmpy2 import mpfr, mpc

from mbrat.commander import Command
from mbrat.configmgr import ConfigManager
from mbrat.mutil import mandelfun



class SigCommand(Command):
    name = "sig"
    description = "Sign a file, or validate a FILE using given MBRAT file. Uses current profile."
    help = "sign or validate a file"

    def __init__(self):
        super(SigCommand, self).__init__()

        self.group_sig = self.parser.add_mutually_exclusive_group()
        self.group_sig.add_argument( 
            "--sign", "-s", action='store_true',
            help="sign the FILE and save signature file" 
        )
        self.group_sig.add_argument( 
            "--valid", "-v", action='store', metavar="MBRAT",
            help="validate the FILE using MBRAT signature file" 
        )
        self.parser.add_argument( 
            "file", action='store',
            help="FILE to sign or validate" 
            )

        self.parser.set_defaults(command=self)

        # init spi for this command 
        self.spi = None

        # instantiate a ConfigManager
        self.cfgmgr = ConfigManager()
        self.config = self.cfgmgr.secmgr['profile']


    def run_command(self, args):
        """ Sign or validate the given file. """

        if not path.exists(args.file):
            return False

        # read the file as plaintext
        with open(args.file, 'r') as f:
            plaintext = f.read()
        args.plaintext = plaintext

        args.spi = {}

        # if signing, just sign
        if args.sign:
            # get the  results as a str to write to file
            args.spi['return_dict'] = False
            sig_cfg = self.run_sign(args)
            cfgf = (path.basename(args.file)).splitext()[0] + '.mbrat'
            with open(cfgf, 'w') as f:
                f.write(sig_cfg)

            return True

        # if validating... read the .cfg-style '.mbrat' file too
        if args.valid:
            if not path.splitext(path.basename(args.valid))[1] == 'mbrat':
                return False

            # get the results as a dict to use
            args.spi['return_dict'] = True
            sig_d = self.run_sign(args)

            return self.run_valid(args)

        # otherwise something went wrong?
        return False


    def run_sign(self, args):

        # instantiate a signing object
        from mbrat.spi.sign import SignSPI
        spi = SignSPI(mandelfun)

        # get needed configs
        privkey_cfg = self.cfgmgr.secmgr['privkey']
        pool_cfg = self.cfgmgr.secmgr['pool']
        poolkey_cfg = self.cfgmgr.secmgr['poolkey']

        # put together arguments for the SPI
        args.spi['iters'] = int(pool_cfg.get('iters')) + int(privkey_cfg.get_from_section('pool', 'iters'))

        # set the precision
        args.spi['prec'] = int(privkey_cfg.get('prec'))
        gmpy2.get_context().precision = args.spi['prec']

        # format the keys for mpc
        args.spi['poolkey'] = mpc( poolkey_cfg.get('real') + " " + poolkey_cfg.get('imag') )
        args.spi['privkey'] = mpc( privkey_cfg.get('real') + " " + privkey_cfg.get('imag') )

        # sign the hash
        hash_sig = spi.run(args)

        # return a dict if desired
        if args.spi['return_dict']:
            return hash_sig

        # return the result to run_command in '.INI' config format
        sig = "# {2:=^76} #\n# {0:^76} #\n# {1:=^76} #\n".format( 
            "{0}:{1}:{2}".format( self.config.get('name'), 
                                  poolkey_cfg.get('name'), 
                                  privkey_cfg.get('name') ),
            "> SNIP <", "=" )

        sig += "[poolkey]\nprec={0}\niters={1}".format(args.spi['prec'], pool_cfg.get('iters')) \
            + "real={0:a}\nimag={1:a}\n".format(args.spi['poolkey'].real, args.spi['poolkey'].imag) \
            + "[signature]\nhash_sig: {0:Ma}".format(hash_sig[0])

        for i in range(len(hash_sig)):
            sig += "\t{0:Ma}".format(hash_sig[i])

        return sig

    
    def run_valid(self, args):

        from mbrat.spi.sign import ValidateSPI
        self.spi = ValidateSPI(mandelfun)

        print "Validating '{0}'\n  -> source pubkey {1} ...".format(
            args.file, args.valid)

        config.read(args.valid)

        # setup the args.spi
        args.spi = {}
        for section in config.sections():
            args.spi[section] = dict(config.items(section))

        isvalid = self.spi.run(args)


# instantiate command
SigCommand()
