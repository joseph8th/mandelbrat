import os
from os import path
from shutil import rmtree
#from mpmath import mp, mpc, nstr
#from mpmath import mpmathify as mpify

from mbrat.commander import ConfigCommand
from mbrat.mscreen import PyMScreen
from mbrat.util import arglist_parse_to_dict
from mbrat.mutil import MandelFun as mfun
from mbrat.mutil import MultiLibMPC as mlmpc


class PrivKeyCommand(ConfigCommand):
    name = "privkey"
    description = "Private key manager."
    help = "private key manager"

    def __init__(self):
        super(PrivKeyCommand, self).__init__()
        self.group.add_argument( "--vipool", action='store_true',
                                 help="view info about private pool for current privkey" )
        self.group.add_argument( "--setpool", nargs='*',
                                 help="set private pool config properties" )
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
        elif args.setpool:
            self.run_setpool(args)
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


    def run_setpool(self, args):
        self.config.set_section_to('pool')
        self.name = self.config.get('name')
        args.set = args.setpool
        self.run_set(args)


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

        print "Generating data for pubkey '{}' ...".format(args.genpub)

        # get the necessary configs
        pool_cfg = self.cfgmgr.secmgr['pool']
        pubkey_cfg = self.cfgmgr.secmgr['pubkey']
        poolkey_cfg = self.cfgmgr.secmgr['poolkey']

        # prepare new pubkey meta for file ops
        pubkeyd = path.join( 
            self.cfgmgr.get_cfg_parentd('privpub'), args.genpub )
        pubkeyf = path.join( 
            pubkeyd, "{}.cfg".format(args.genpub) )

        try:
            os.mkdir(pubkeyd)
        except OSError:
            print "==> Modifying '{}' ...".format(args.genpub)

        # set up the necessary values and types
        #        priv_prop_l = arglist_parse_to_dict( self.config.items() ).keys()
        #        if 'prec' in priv_prop_l:
        #            dps = int( self.config.get('prec') )
        #            mp.dps = dps
        #        else:
        #            dps = mp.dps

        # poolkey = mpc( real = mpify(poolkey_cfg.get('real')),
        #             imag = mpify(poolkey_cfg.get('imag')) )
        # privkey = mpc( real = mpify(self.config.get('real')),
        #             imag = mpify(self.config.get('imag')) )

        poolkey = mlmpc( x = poolkey_cfg.get('real'),
                         y = poolkey_cfg.get('imag'),
                         prec = self.config.get('prec') )

        privkey = mlmpc( real = self.config.get('real'),
                         imag = self.config.get('imag'),
                         prec = self.config.get('prec') )

        pooliters = int( pool_cfg.get('iters') )
        priviters = pooliters + int( 
            self.config.get_from_section('pool', 'iters') )

        # generate the pubkey, make property dict, write_set to new config
        pubkey = mfun().run( poolkey, poolkey, privkey, priviters )

        prop_d = { 
            'pubkey': {
                'name': args.genpub, 
                'info': "Using PrivKey '{0}' and PoolKey '{1}'".format(
                    self.config.get('name'), poolkey_cfg.get('name') ),
                'real': nstr( pubkey.real, dps ), 
                'imag': nstr( pubkey.imag, dps ), 
                },
            'poolkey': {
                'name': poolkey_cfg.get('name'),
                'pool': pool_cfg.get('name'),
                },
            'privkey': {
                'real': nstr( privkey.real, dps ),
                'imag': nstr( privkey.imag, dps ),
                'prec': dps,
                },
            }
        pubkey_cfg.set_write_configf( pubkeyf, prop_d['pubkey'] )
        pubkey_cfg.set_write_to_section( 'poolkey', prop_d['poolkey'] ) 
        self.config.set_write( prop_d['privkey'] )

        # output the results
        print "==> Wrote to pubkey '{}' at".format(args.genpub)
        print "  -> {}".format(pubkeyf)
        print "==> Parameters used:\n  -> PoolKey =", poolkey, \
            "\n  -> PrivKey =", privkey
        print "  -> Private Max. Iterations = {}".format(priviters)
        print "  -> Private Precision = {}".format(dps)
        print "==> PubKey generated (n,E):", \
            "\n  -> n = {}".format(pooliters), \
            "\n  -> E =", pubkey
        


# instantiate command
PrivKeyCommand()
