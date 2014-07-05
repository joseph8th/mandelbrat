from os import path
import gmpy2
from gmpy2 import mpfr, mpc
import ConfigParser

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
            "--valid", "-v", nargs='?', metavar="MBRAT",
            help="validate the FILE [optional: using specified MBRAT signature file path]" 
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
        self.cfgparser = ConfigParser.RawConfigParser()

        # get needed configs
        self.privkey_cfg = self.cfgmgr.secmgr['privkey']
        self.pool_cfg = self.cfgmgr.secmgr['pool']
        self.poolkey_cfg = self.cfgmgr.secmgr['poolkey']



    def run_command(self, args):
        """ 
        Sign or validate the given file. 
        """

        if not path.exists(args.file):
            return False

        # read the file as plaintext
        with open(args.file, 'r') as f:
            plaintext = f.read()
        args.plaintext = plaintext

        args.spi = {}

        # sign or validate ...
        if args.sign:
            return self.run_sign(args)
        else:
            return self.run_valid(args)

        # otherwise something went wrong?
        return False


    def _write_sig_config(self, sig_d, sig_cfgf):

        # otherwise write the result to run_command in '.INI' config format
        for sec, sec_d in sig_d.iteritems():
            self.cfgparser.add_section(sec)

            # check for special formatting of elts in dict
            for key, val in sec_d.iteritems():
                if val.__class__.__name__ == 'mpc':
                    self.cfgparser.set( sec, key, "{:Me}".format(val))
                elif isinstance(val, list):
                    self.cfgparser.set( sec, key, "\n\t".join(["{:Me}".format(v) for v in val]) )
                else:
                    self.cfgparser.set( sec, key, str(val))

        # write to the cfg file
        with open(sig_cfgf, 'wb') as configfile:
            self.cfgparser.write(configfile)


    def run_sign(self, args, return_dict=False):
        """ 
        Method to sign a hash of a given file, returning either True or a dict if return_dict==True.
        """

        from mbrat.spi.sign import SignSPI
        spi = SignSPI(mandelfun)

        print "Signing '{0}' with profile '{1}:{2}' and pool '{3}:{4}' ...".format(
            args.file, self.config.get('name'), self.privkey_cfg.get('name'),
            self.pool_cfg.get('name'), self.poolkey_cfg.get('name')
            )

        # put together arguments for the SPI
        args.spi['iters'] = int(self.pool_cfg.get('iters')) + \
            int(self.privkey_cfg.get_from_section('pool', 'iters'))

        # set the precision
        args.spi['prec'] = int(self.privkey_cfg.get('prec'))

        gmpy2.get_context().precision = args.spi['prec']

        # format the keys for mpc
        args.spi['poolkey'] = mpc( self.poolkey_cfg.get('real') + " " \
                                   + self.poolkey_cfg.get('imag') )
        args.spi['privkey'] = mpc( self.privkey_cfg.get('real') + " " \
                                   + self.privkey_cfg.get('imag') )

        ######## sign the hash ########
        hash_sig = spi.run(args)

        # init a ConfigParser compat dict with a top-section of 'mhash'
        sig_d = {'mhash': {'prec': args.spi['prec']}}

        for sec in ['pool', 'poolkey']:
            sig_d[sec] = self.cfgmgr.secmgr[sec].get_as_args(
                subsection=sec, return_dict=True)

        sig_d['signature'] = { 'hash_sig': hash_sig }        # add hash_sig

        # return a dict if desired ...
        if return_dict:
            return sig_d

        # ... or get the filename for the signature 'BASENAME.mbrat' file
        sig_cfgf = path.splitext(path.basename(args.file))[0] + ".mbrat"
        sig_cfgf = path.join( path.dirname(path.abspath(args.file)), 
                              sig_cfgf )

        self._write_sig_config(sig_d, sig_cfgf)

        return True


    ## VALIDATION section ##

    def _read_sighash_config(self, sig_cfgf):

        # get pool/poolkey config from given .mbrat file
        self.cfgparser.read(path.abspath(sig_cfgf))

        print path.abspath(sig_cfgf)


        # set precision try
        try:
            prec = self.cfgparser.getint('poolkey', 'prec')
        except ConfigParser.NoOptionError:
            return None

        gmpy2.get_context().precision = prec

        # check to see if the poolkey already exists, else create it
#        sig_pool = 

        sig_d = {}
        for sec in self.cfgparser.sections():
            if sec == 'poolkey':
                sig_d[sec] = { 'name': self.cfgparser.get(sec, 'name'), 
                               'prec': prec,
                               'iters': self.cfgparser.getint(sec, 'iters'),
                               'mpoint': mpc( self.cfgparser.get(sec, 'mpoint') ),
                               }
            elif sec == 'signature':
                hash_sig_s = self.cfgparser.get(sec, 'hash_sig')
                sig_d[sec] = { 'hash_sig': [mpc(pt) for pt in hash_sig_s.split('\n')] }

        return sig_d


    def run_valid(self, args):
        """
        Validate a given file using a given '.mbrat' signature config file.
        """

        from mbrat.spi.sign import ValidateSPI
        self.spi = ValidateSPI(mandelfun)

        if not args.valid:
            sig_cfgf = path.splitext(path.basename(args.file))[0] + ".mbrat"
            args.valid = path.join( path.dirname(path.abspath(args.file)), 
                                    sig_cfgf )

        print "Validating '{0}'\n  -> With received signed hash: {1} ...".format(args.file, args.valid)

        # first read THEIR signed hash '*.mbrat' and deal with it
        if not path.splitext(path.basename(args.valid))[1] == '.mbrat':
            return False

        their_sig = self._read_sighash_config(args.valid)

        if not their_sig:
            print "Error: unable to read: {}".format(args.valid)
            return False

        print their_sig

        # then mhash the plaintext for comparison
        my_sig = self.run_sign(args, return_dict=True)
#############33
        print my_sig


        # setup the args.spi
#       args.spi = {}


#       isvalid = self.spi.run(args)


# instantiate command
SigCommand()
