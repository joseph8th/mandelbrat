import os
from os import path
from sys import modules
from os.path import join, splitext
from shutil import rmtree

from mbrat.argparser import subparsers
from mbrat import commands
from mbrat.configmgr import ConfigManager
from mbrat.mscreen import PyMScreen
from mbrat.util import arglist_parse_to_dict


class Command(object):
    """
    Parent class for command-line commands. """

    name = None
    description = ""
    help = ""

    def __init__(self):
        self.parser = subparsers.add_parser(name = self.name,
                                            description = self.description, 
                                            help = self.help)
    def run(self, args):
        self.run_command(args)


class ConfigCommand(object):
    """
    Parent class for profile configuration commands. """

    name = None
    description = ""
    help = ""
#    make = None

    def __init__(self):
        self.parser = subparsers.add_parser(name = self.name,
                                            description = self.description, 
                                            help = self.help)

        self.group = self.parser.add_mutually_exclusive_group()
        self.group.add_argument( "--ls", action='store_true',
                                 help="list available {}(s)".format(self.name) )
        self.group.add_argument( "--vi", action='store_true',
                                 help="view info about current {}".format(self.name) )
        self.group.add_argument( "--mk", action='store',
                                 help="create a new {} with given name".format(self.name) )
        self.group.add_argument( "--rm", action='store', 
                                 help="remove a {}".format(self.name) )
        self.group.add_argument( "--ck", action='store', 
                                 help="checkout the given {}".format(self.name) )
        self.group.add_argument( "--set", nargs='*',
                                 help="set current {} config properties".format(self.name) )

        # instantiate a ConfigManager and set 'config' attr to manage this section 
        self.cfgmgr = ConfigManager()
        self.config = self.cfgmgr.secmgr[self.name]


    def run(self, args):
        """
        Sends preset parsed arguments to given subcommand's run_command()
        """
        if args.vi:
            self.run_vi(args)
        elif args.mk:
            self.run_mk(args)
        elif args.ck:
            self.run_ck(args)
        elif args.set:
            self.run_set(args)
        else:
            self.run_command(args)


    def run_ls(self, args):
        if self.name == 'pubkey':
            # since published pubkeys aren't contained in separate dirs
            cur_cfg = self.cfgmgr.get_current_cfg(self.name)
        else:
            cur_cfg = self.cfgmgr.get_current_cfg(self.name, dironly=True)
        cur_cfg = path.basename(cur_cfg)
        parentd = self.cfgmgr.get_cfg_parentd(self.name)
        print "Listing '{0}' in\n--> {1} ...\n".format(self.name, parentd)
        for cfg in self.cfgmgr.get_cfg_list(self.name):
            cfg += "*" if cfg == cur_cfg else ""
            print "\t{}".format(cfg)


    def run_vi(self, args):
        print "Current {}:\n".format(self.name)
        for prop, val in self.config.items():
            print "\t{0} = {1}".format( prop, val )


    def run_mk(self, args):
        print "Making {0} '{1}' ...".format(self.name, args.mk)
        if not self.cfgmgr.make_config( self.name, args.mk ):
            exit( "==> ERROR: unable to make '{}'".format(args.mk) )


    def run_rm(self, args, cfglink=False):
        print "Removing {0} '{1}' ...".format(self.name, args.rm)            
        if args.rm == self.config.get('name'):
            exit( "==> ERROR: cannot remove current {0} '{1}'".format(self.name, args.rm) )

        if cfglink:
            # get a link to a config file, ie for pubkey
            config = self.cfgmgr.get_configf(self.name, "{}.cfg".format(args.rm), 
                                             cfglink=True)
        else:
            # get the config dir itself
            config = self.cfgmgr.get_configf(self.name, args.rm, 
                                             dironly=True)
        if not config:
            exit( "==> ERROR: {0} '{1}' does not exist".format(self.name, args.rm) )

        if cfglink:
            # remove just the link file...
            os.remove(config)
        else:
            # ... or the whole directory
            rmtree( config, ignore_errors=True )

        if not path.exists(config):
            print "==> Deleted: {}".format(config)
        else:
            exit( "==> ERROR: failed to delete {}".format(config) )


    def run_ck(self, args):
        print "Checking Out {0} '{1}' ...".format(self.name, args.ck)
        if not self.cfgmgr.set_current_cfg_by_name( self.name, args.ck ):
            exit( "==> ERROR: {0} '{1}' not found".format(self.name, args.ck) )


    def run_set(self, args):
        print "Setting {} properties ...".format(self.name)
        prop_d = arglist_parse_to_dict(args.set)
        self.config.set_write(prop_d)


    def run_pkrand(self, args):
        """
        A *key-only method to pick a random point from a pool (MScreen). """
 
        print "Picking a random {} key-point ...".format(self.name)
        pool_cfg = self.cfgmgr.secmgr['pool']

        # public poolkey pool or not? (ie, privkey pool)
        if 'pool' in self.name:
            pool_t = 'pool'
            additers = 0
            keypool_cfg = pool_cfg
        else:
            pool_t = self.name
            additers = pool_cfg.get('iters')
            keypool_cfg = self.config
            keypool_cfg.set_section_to('pool')
            keypool_cfg.read()

        args = keypool_cfg.get_as_args()
        args.iters = int(args.iters) + int(additers)
        ms = PyMScreen(args)
        print ms.get_info()

        imgf = keypool_cfg.get('image')
        if not imgf or not path.exists(imgf):
            # generate pool image file from MScreen and attach to config file ...
            imgf = path.join( keypool_cfg.rootd, "{}.png".format(keypool_cfg.get('name')) )
            print "==> {} pool image not found. Making new at".format(self.name)
            print "--> {} ...".format(imgf)
            ms.gen_to_file(imgf)
            keypool_cfg.set_write( {'image': imgf,} )

        else:
            # ... else read PyMScreen object from image file
            print "Reading image file ..."
            try:
                ms.gen_mscreen_from_img(imgf)
            except Exception, err:
                exit( "==> ERROR: {}".format(str(err)) )

        # MScreen method returns a random MPoint object
        pt = ms.get_mpoint()
        print "==> Point picked: (x,y) = ", pt.c
        # update current *key config file
        self.config.reset_section()
        self.config.set_write( {'real': pt.real, 'imag': pt.imag,} )


### load subcommands funcs ###

def _load_command(name):
    command = 'mbrat.commands.%s' % name
    if command in modules:
        return
    try:
        __import__(command)
    except ImportError:
        print "ImportError: unable to import %s" % command
#        pass

def get_cmd_list():
    """
    Assumes /commands/*.py are commands if '__' is not in filename.
    """
    return [fname for fname, fext in map( splitext, 
                                          os.listdir(join(os.getcwd(), 'mbrat/commands')) )
            if fext == '.py' and '__' not in fname]


def load_commands():
    """
    Load all commands.
    """
    cmd_l = get_cmd_list()
    for name in cmd_l:
        _load_command(name)
