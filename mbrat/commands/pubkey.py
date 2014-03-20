from os import path
from mbrat.commander import ConfigCommand


class PubKeyCommand(ConfigCommand):

    name = "pubkey"
    description = "Public key manager."
    help = "public key manager"


    def __init__(self):

        super(PubKeyCommand, self).__init__()

        self.pubkey_group = self.parser.add_argument_group("subcommand group", "subcommand-specific options")
        self.pubkey_group.add_argument( "--unpub", action='store_true', dest="lspub",
                                 help="list unpublished public keys for current config" )
        self.pubkey_group.add_argument( "--genpub", action='store',
                                 help="generate an unpublished public key using current config" )
        self.pubkey_group.add_argument( "--rmpub", action='store',
                                 help="delete an unpublished public key" )

        self.parser.set_defaults(command=self)


    def run_command(self, args):
        if args.rm:
            self.run_rm(args, cfglink=True)
        elif args.lspub:
            self.run_lspub(args)
        elif args.genpub:
            self.run_genpub(args)
        elif args.rmpub:
            self.run_rmpub(args)


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
        pubkey = mandelfun( poolkey, poolkey, privkey, priviters )

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
PubKeyCommand()
