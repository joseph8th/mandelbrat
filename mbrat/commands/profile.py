import os
from os import path
from shutil import rmtree, copytree, Error

from mbrat.commander import ConfigCommand
from mbrat.settings import MBRAT_PROFILESD
from mbrat.util import arglist_parse_to_dict


class ProfileCommand(ConfigCommand):
    name = "profile"
    description = "MBrat user profile manager."
    help = "user profile manager"

    def __init__(self):
        super(ProfileCommand, self).__init__()
        self.group.add_argument( "--cp", action='store',
                                 help="copy current profile to given name" )
        self.parser.set_defaults(command=self)


    def run_cp(self, args):
        new_profiled = path.join( MBRAT_PROFILESD, args.cp )
        if path.exists(new_profiled):
            exit( "==> ERROR: User Profile '{}' already exists.".format(args.cp) )

        cur_profile = self.config.get('name')
        cur_profiled = self.config.rootd
        print "Copying User Profile '{0}' to '{1}'...".format(cur_profile, args.cp)
        print "==> '{0}'\n--> '{1}'".format(cur_profiled, new_profiled)
        try:
            copytree( cur_profiled, new_profiled, symlinks=True )
        except Error:
            exit( "==> ERROR: Unable to copy '{}'.".format(cur_profile) )

        print "Configuring User Profile..."

        # remove the old profile config file...
        try:
            os.remove( path.join(new_profiled, path.basename(self.config.configf)) )
        except OSError:
            exit( "==> ERROR: could not remove old config file." )
        # ...and make a new one...
        prop_d = { 'info': "Use 'profile --set' option to alter profile.",
                   'name': args.cp, }
        configf = path.join( new_profiled, "{}.cfg".format(args.cp) )
        self.config.set_write_configf( configf, prop_d )
        self.cfgmgr.set_current_cfg( MBRAT_PROFILESD, configf )
        
        # now rebuild '_current' symlinks for keys (default: 1st key found)...
        datad = path.join( new_profiled, 'data' )
        privname = self.cfgmgr.get_cfg_list('privkey')[0]
        privf = self.cfgmgr.get_configf('privkey', privname)
        # ...set _current to new configf...
        self.cfgmgr.set_current_cfg( datad, privf )
        # ...wipe out 'image' value in privkey 'pool' section...
        self.cfgmgr.secmgr['privkey'].set_write_to_section( 'pool', {'image': "",} )

        # now do the 'same' for pubkey links...
        publicd = path.join( new_profiled, 'public' )
        pubfname = self.cfgmgr.get_cfg_list('pubkey')[0]
        pubname, ext = path.splitext(pubfname)
        pubkeyl = path.join( publicd, pubfname )
        privpubd = path.join( datad, privname, 'public', pubname )
        privpubf = path.join( privpubd, pubfname )
        try:
            os.remove( pubkeyl )
        except OSError:
            exit( "==> ERROR: could not remove old pubkey link to config file." )
        os.symlink( privpubf, pubkeyl )
        # ... set current to publicized symlink to private pubkey file
        self.cfgmgr.set_current_cfg( publicd, pubkeyl ) 

        # at last re-read the config
        self.config.read()


    def run_command(self, args):
        if args.rm:
            self.run_rm(args)
        elif args.cp:
            self.run_cp(args)
        else:
            self.run_ls(args)


# instantiate command
ProfileCommand()
