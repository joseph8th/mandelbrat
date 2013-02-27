import os
from os import path
from shutil import rmtree

from mbrat.commander import ConfigCommand
from mbrat.mscreen import PyMScreen
from mbrat.util import pyMFun


class PrivKeyCommand(ConfigCommand):
    name = "privkey"
    description = "Private key manager."
    help = "private key manager"

    def __init__(self):
        super(PrivKeyCommand, self).__init__()
        self.group.add_argument( "--vipool", action='store_true',
                                 help="view info about private pool for current privkey" )
        self.group.add_argument( "--pkrand", action='store_true',
                                 help="pick a random private key-point from private pool" )
        self.group.add_argument( "--lspub", action='store_true',
                                 help="list unpublished public keys" )
        self.group.add_argument( "--genpub", action='store',
                                 help="generate public key 'GENPUB' using current config" )
        self.group.add_argument( "--rmpub", action='store',
                                 help="delete unpublished public key 'RMPUB" )

        self.parser.set_defaults(command=self)


    def run_command(self, args):
        if args.rm:
            self.run_rm(args)
        elif args.vipool:
            self.run_vipool(args)
        elif args.pkrand:
            self.run_pkrand(args)
        elif args.lspub:
            self.run_lspub(args)
        elif args.genpub:
            self.run_genpub(args)
        elif args.rmpub:
            self.run_rmpub(args)
        else:
            self.run_ls(args)


    def run_vipool(self, args):
        self.config.set_section_to('pool')
        self.name = self.config.get('name')
        self.run_vi(args)


    def run_lspub(self, args):
        self.name = 'privpub'
        self.run_ls(args)


    def run_rmpub(self, args):
        "Removing unpublished pubkey '{}' ...".format(args.rmpub)
        if not args.rmpub in self.cfgmgr.get_cfg_list('privpub'):
            exit( "==> ERROR: pubkey '{}' does not exist".format(args.rmpub) )
        privpubd = path.join( self.cfgmgr.get_cfg_parentd('privpub'), args.rmpub )
        rmtree( privpubd, ignore_errors=True )
        if not path.exists(privpubd):
            print "==> Deleted '{}'".format(privpubd)


    def run_genpub(self, args):
        # get the necessary configs
        pool_cfg = self.cfgmgr.secmgr['pool']
        pubkey_cfg = self.cfgmgr.secmgr['pubkey']
        poolkey_cfg = self.cfgmgr.secmgr['poolkey']

        # prepare new pubkey meta for file ops
        pubkeyd = path.join( self.cfgmgr.get_cfg_parentd('privpub'), args.genpub )
        pubkeyf = path.join( pubkeyd, "{}.cfg".format(args.genpub) )
        try:
            os.mkdir(pubkeyd)
        except OSError:
            exit( "==> ERROR: pubkey '{}' already exists.".format(args.genpub) )

        # set up the necessary values and types
        poolkey = complex( float(poolkey_cfg.get('real')),
                           float(poolkey_cfg.get('imag')) )
        privkey = complex( float(self.config.get('real')), 
                           float(self.config.get('imag')) )
        pooliters = int( pool_cfg.get('iters') )
        priviters = pooliters + int( self.config.get_from_section('pool', 'iters') )

        # generate the pubkey, make property dict, write_set to new config file...
        pubkey = pyMFun( poolkey, poolkey, privkey, priviters )
        prop_d = { 
            'pubkey': {
                'name': args.genpub, 
                'info': "Made with PrivKey '{0}' and PoolKey '{1}'".format(
                    self.config.get('name'), poolkey_cfg.get('name') ),
                'real': pubkey.real, 'imag': pubkey.imag, 
                },
            'poolkey': {
                'name': poolkey_cfg.get('name'),
                'pool': pool_cfg.get('name'),
                },
            }
        pubkey_cfg.set_write_configf( pubkeyf, prop_d['pubkey'] )
        pubkey_cfg.set_write_to_section( 'poolkey', prop_d['poolkey'] ) 

        # output the results
        print "Generating unpublished pubkey '{}' to".format(args.genpub)
        print "--> {} ...\n".format(pubkeyf)
        print "\tPoolKey =", poolkey, "\n\tPrivKey =", privkey
        print "\tPrivate Max. Iterations = {}".format(priviters)
        print "\n==> PubKey = [", pubkey, ", {} ]".format(pooliters)
        


# instantiate command
PrivKeyCommand()
