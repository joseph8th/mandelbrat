import os
from os import path
import ConfigParser

from mbrat.util import Arguments, arglist_parse_to_dict, mb_mkdirs, clogger
from mbrat.settings import MBRAT_USRD, MBRAT_USR_CFGF, MBRAT_POOLSD, MBRAT_PROFILESD, \
    MBRAT_CURRENTL, MBRAT_DEF_POOL_D, MBRAT_DEF_POOLKEY_D, MBRAT_DEF_PRIVKEY_D, MBRAT_DEF_USR_D, \
    MBRAT_TMPD, MBRAT_TMPF, MBRAT_CFG_TYPE_L, MBRAT_CFG_DEPTREE_D


class SecManager(object):
    """
    ConfigParser manager per top section (section.cfg). """

    def __init__(self, section, configf):
        self.cfg_t = section
        self.set_section_configf(section, configf)
        self._init_config()

    def _init_config(self):
        self.config = ConfigParser.ConfigParser()
        self.config.add_section(self.section)
        self.read()

    # top-level object attr accessors/mutators 

    def set_section_configf(self, section, configf):
        self.section = section
        self.configf = configf
        self.rootd = path.dirname(self.configf)
        self.parentd = path.dirname(self.rootd)

    def get_configf_by_name(self, cfgname):
        configf = path.join( self.parentd, cfgname, "{}.cfg".format(cfgname) )
        if not path.exists(configf):
            return None
        return configf

    def set_configf(self, configf):
        self.reset_section()
        self.set_section_configf(self.section, configf)

    def set_configf_by_name(self, cfgname):
        configf = self.get_configf_by_name(cfgname)
        if configf:
            self.set_configf(configf)
            return True
        return False

    def set_write_configf(self, configf, prop_d):
        self.set_configf(configf)
        self.set_write(prop_d)

    def add_section(self, section):
        self.config.add_section(section)

    def sections(self):
        return self.config.sections()

    def set_section_to(self, subsection):
        if subsection in self.sections():
            self.section = subsection

    def reset_section(self):
        self.section = self.cfg_t

    # primary ConfigParser management methods

    def write(self):
        with open( self.configf, 'wb' ) as configfile:
            self.config.write(configfile)

    def read(self):
        self.config.read(self.configf)

    def get_from_section(self, section, key):
        if not path.exists(self.configf):
            return None
        self.read()
        return self.config.get( section, key )

    def get(self, key):
        return self.get_from_section( self.section, key )

    def set_in_section(self, section, key, val):
        if not section in self.sections():
            self.add_section(section)
        self.config.set( section, key, val )

    def set(self, key, val):
        self.set_in_section( self.section, key, val )

    def set_write_to_section(self, section, prop_d):
        for prop, val in prop_d.iteritems():
            self.set_in_section( section, prop, val )
        self.write()

    def set_write(self, prop_d):
        self.set_write_to_section( self.section, prop_d )

    def items_in_section(self, section):
        return self.config.items(section)

    def items(self):
        return self.items_in_section(self.section)

    # secondary accessors/mutators

    def get_as_args(self, subsection=None, return_dict=False):
        if subsection:
            self.set_section_to(subsection)
        self.read()
        arg_d = arglist_parse_to_dict(self.items())

        if return_dict:
            return arg_d

        return Arguments(arg_d)
        


class ConfigManager(object):
    """
    file/dir-level MBrat configuration manager. """

    def __init__(self, profilename=None, usr_cfgf=None):
        self.err = ""
        self.log = ""
        self._init_usr_config(usr_cfgf)
        self._init_section_managers(profilename)


    def _init_usr_config(self, usr_cfgf):

        # init base config paths
        self.usrcfg = {}
        if not usr_cfgf:
            self.usrcfg['path'] = MBRAT_USRD
            self.usrcfg['cfgf'] = MBRAT_USR_CFGF
        else:
            self.usrcfg['path'] = path.dirname(usr_cfgf)
            self.usrcfg['cfgf'] = path.abspath(usr_cfgf)

        self.tmpcfg = { 'path': path.join( self.usrcfg['path'], 'tmp' ) }
        self.tmpcfg['cfgf'] = path.join( self.tmpcfg['path'], 'tmp.cfg' )
        self.tmpcfg['imgf'] = path.join( self.tmpcfg['path'], 'tmp.png' )

        self.poolsd = path.join( self.usrcfg['path'], 'pools' )
        self.profilesd = path.join( self.usrcfg['path'], 'profiles' )

        # define secmgr dict and run sanity check on config
        self.secmgr = {}
        self.sanity_check()


    def sanity_check(self):
        """ Method to check dir tree structure and config file integrity. """

        # make sure 'usr' dir tree is intact & create anew if not
        for d in [self.usrcfg['path'], self.tmpcfg['path'], self.poolsd, self.profilesd]:
            if not path.exists(d):
                if not mb_mkdirs(d):
                    return self._err("==> ERROR: Unable to create '{}'".format(d) )
                self._log("==> Created new directory at\n  -> {}".format(d) )

        # make sure '.cfg' files exist for 'usr', 'tmp' and 'skel*' & make if not
        if not path.isfile( self.usrcfg['cfgf'] ):
            prop_d = MBRAT_DEF_USR_D.copy()
            self.usrmgr = SecManager('prefs', self.usrcfg['cfgf'])
            self.usrmgr.set_configf( self.usrcfg['cfgf'] )
            self.usrmgr.set_write( prop_d['prefs'] )
            self._log("==> Created new usr.cfg at\n  -> {}".format(self.usrcfg['cfgf']) )

        if not path.isfile( self.tmpcfg['cfgf'] ):
            self.secmgr['tmp'] = SecManager('tmp', self.tmpcfg['cfgf'])
            self._mkcfg_tmp()
            self._log("==> Created new tmp.cfg at\n  -> {}".format(self.tmpcfg['cfgf']) )

        # skel* and _current sanity - iters over [pool, poolkey, profile, privkey,..]
        for cfg_t in [t for t in MBRAT_CFG_TYPE_L if t != 'pubkey']:
            cfgname = "skel{}".format(cfg_t)
            cfg_parentd = self.get_cfg_parentd(cfg_t)
            configf = path.join( cfg_parentd, cfgname, "{}.cfg".format(cfgname) )
            cfg_l = os.listdir(cfg_parentd)

            if not cfgname in cfg_l:
                self.secmgr[cfg_t] = SecManager( cfg_t, configf )
                self.make_config( cfg_t, cfgname, update=False, current=False )
                self._log(
                    "==> Created skeleton '{0}' config at\n  -> {1}".format(cfg_t, configf)
                )

            if not MBRAT_CURRENTL in cfg_l:
                current_cfg = path.join( cfg_parentd, MBRAT_CURRENTL )
                os.symlink( configf, current_cfg )


    def _init_section_managers(self, profilename):

        # user 'mbrat' preferences esp for GUI
        self.usrmgr = SecManager('prefs', self.usrcfg['cfgf'])

        # 'usr/' tree configs
        self._init_profile(profilename)
        self.secmgr = {
            'profile': SecManager('profile', self.profile_cfg),
            'pool': SecManager('pool', self.get_current_cfg('pool')),
            'poolkey': SecManager('poolkey', self.get_current_cfg('poolkey')),
            'privkey': SecManager('privkey', self.get_current_cfg('privkey')),
            'pubkey': SecManager('pubkey', self.get_current_cfg('pubkey')),
            'tmp': SecManager('tmp', self.tmpcfg['cfgf']),
            }

    def _update_section_managers(self):
        for cfg_t in MBRAT_CFG_TYPE_L:
            self.secmgr[cfg_t].set_configf( self.get_current_cfg(cfg_t) )
            self.secmgr[cfg_t].read()

    def _init_profile(self, profilename):
        # default init to current profile if given not found
        if profilename:
            configf = self.get_configf('profile', profilename)
            if configf:
                self.set_current_cfg( self.profilesd, configf )
                self._log("==> Activated profile '{}'".format(profilename) )
        self.profile_cfg = self.get_current_cfg('profile')


    # log & err methods

    def _err(self, msg):
        self.err += "{}\n".format(msg)
        return False

    def errstr(self):
        errstr = self.err
        self.err = ""
        return errstr
    
    def _log(self, msg):
        self.log += "{}\n".format(msg)

    def logstr(self):
        logstr = self.log
        self.log = ""
        return logstr


    # primary getters/setters

    def set_current_cfg(self, targetd, configf, update=True):
        """
        Set '_current' configf for any target directory. Doesn't use SecManager. """

        current_cfg = os.path.join( targetd, MBRAT_CURRENTL )
        try:
            os.remove(current_cfg)
        except OSError:
            pass
        os.symlink( configf, current_cfg )

        # re-initialize the SecManager dict
        if update:
            self._update_section_managers()


    def set_current_cfg_by_name(self, cfg_t, cfgname):
        """
        Set '_current' configf by top-section and name. Uses SecManager methods. 
        Cascades dependencies to set correct current config in 'child' SecManager(s).
        For example: set 'profile' -> set ['privkey', 'pubkey'] 

        """

        # this part updates the approp. SecManager(s)
        if not self.secmgr[cfg_t].set_configf_by_name(cfgname):
            return False
        self.secmgr[cfg_t].read()

        self.set_current_cfg( self.secmgr[cfg_t].parentd, 
                              self.secmgr[cfg_t].configf )
        return True


    def get_configf(self, cfg_t, cfgname, dironly=False, cfglink=False):
        """
        Get configf from dir structure, not SecManager methods. """
        
        # is there even a dir named cfgname?
        if not cfgname in self.get_cfg_list(cfg_t):
            return None

        # cfglink True means a pubkey.cfg symlink
        if cfglink:
            configf = path.join( self.get_cfg_parentd(cfg_t), cfgname )
        else:
            configf = path.join( self.get_cfg_parentd(cfg_t), cfgname, 
                                 "{}.cfg".format(cfgname) )
        # check for file
        if not path.exists(configf):
            return None

        # dironly True if only the containing dir is desired
        if dironly:
            return path.dirname(configf)

        return configf


    # secondary config accessors/mutators/generators/factories

    def get_cfg_list(self, cfg_t):
        parentd = self.get_cfg_parentd(cfg_t)
        return [ p for p in os.listdir(parentd) if not '_' in p[0] ]


    def get_cfg_parentd(self, cfg_t):
        if cfg_t == 'usr':
            return self.usrcfg['path']
        elif cfg_t == 'tmp':
            return self.tmpcfg['path']
        elif cfg_t == 'pool':
            return self.poolsd
        elif cfg_t == 'poolkey':
            return path.join( self.get_current_cfg('pool', dironly=True), 'data' )
        elif cfg_t == 'profile':
            return self.profilesd
        elif cfg_t == 'privkey':
            return path.join( self.get_current_cfg('profile', dironly=True), 'data' )
        elif cfg_t == 'pubkey':
            return path.join( self.get_current_cfg('profile', dironly=True), 'public' )
        elif cfg_t == 'privpub':
            return path.join( self.get_current_cfg('privkey', dironly=True), 'public' )


    # special private function to make the temp configf
    def _mkcfg_tmp(self):
        if not path.exists( self.tmpcfg['path'] ):
            os.mkdir( self.tmpcfg['path'] )
        prop_d = MBRAT_DEF_POOL_D.copy()
        prop_d['tmp'] = {'name': "tmp", 'info': "The temp pool."}
        prop_d['pool'].update( {'name': "tmp_pool"} )
        self.secmgr['tmp'].set_configf( self.tmpcfg['cfgf'] )
        self.secmgr['tmp'].set_write(prop_d['tmp'])
        self.secmgr['tmp'].set_write_to_section('pool', prop_d['pool'])


    # ugly 'private' method to reduce repetition in make_config
    def _mkcfg_args(self, cfgname, targetd, subd_l, prop_d):
        configd = path.join( targetd, cfgname )
        args_d = {
            'cfgname': cfgname, 'configd': configd,
            'configf': path.join( configd, "{}.cfg".format(cfgname) ), 
            'mksubd_l': [ path.join(configd, subd) for subd in subd_l ],
            'targetd': targetd, 'prop_d': prop_d,
            }
        return args_d


    # ugly 'private' method to make configs, except pubkeys and tmp
    def _mkcfg(self, cfg_t, args, update, current):
        if not path.exists(args['configd']):
            os.mkdir(args['configd'])
        else:
            return self._err( "==> ERROR: %s '%s' already exists." % \
                              (cfg_t, args['cfgname']) )

        # ... make any subdirs needed...
        for subd in args['mksubd_l']:
            os.mkdir(subd)

        # set_write to new cfg file
        self.secmgr[cfg_t].set_configf(args['configf'])
        for section, prop_d in args['prop_d'].iteritems():
            self.secmgr[cfg_t].set_write_to_section(section, prop_d)

        # set new cfg to _current ?
        if current:
            self.set_current_cfg( args['targetd'], args['configf'], update )

        return True


    # diff method b/c no .cfg file is created or updated, just linked
    def _mkcfg_pubkey(self, cfgname, update, current):

        # each privkey dir has a 'public' dir with PRIVATE pubkey dirs & .cfg's
        cur_privd = self.get_current_cfg('privkey', dironly=True)
        pri_pubd = path.join( cur_privd, 'public' )
        pri_pubkeyf = path.join( pri_pubd, cfgname, "{}.cfg".format(cfgname) )
        if not path.exists(pri_pubkeyf):
            return self._err( "==> ERROR: pubkey '%s' not found." % (cfgname) )

        # each profile has a 'public' dir with PUBLIC pubkey links and _current ln
        pub_pubd = self.get_cfg_parentd('pubkey')
        pub_pubkeyf = path.join( pub_pubd, "{}.cfg".format(cfgname) )
        if path.exists( pub_pubkeyf ):
            return self._err( "==> ERROR: pubkey '%s' already exists." % (cfgname) )

        # symlink the private pubkey .cfg into profile's 'public' dir
        os.symlink( pri_pubkeyf, pub_pubkeyf )

        # set new cfg to _current ?
        if current:
            self.set_current_cfg( pub_pubd, pub_pubkeyf, update )

        return True


    def make_config(self, cfg_t, cfgname, update=True, current=True):
        """
        Method to create complete new default config structure. """

        if cfg_t == 'pool':
            prop_d = MBRAT_DEF_POOL_D.copy()
            prop_d[cfg_t].update( {'name': cfgname,} )
            args = self._mkcfg_args( cfgname, self.poolsd, ['data',], prop_d ) 

        elif cfg_t == 'poolkey':
            targetd = self.get_cfg_parentd(cfg_t)
            prop_d = MBRAT_DEF_POOLKEY_D.copy()
            prop_d[cfg_t].update( {'name': cfgname,} )
            args = self._mkcfg_args( cfgname, targetd, [], prop_d )

        elif cfg_t == 'profile':
            prop_d = { cfg_t: {'info': "", 'name': cfgname,}, }
            args = self._mkcfg_args( cfgname, self.profilesd, ['data', 'public',], prop_d )

        elif cfg_t == 'privkey':
            targetd = self.get_cfg_parentd(cfg_t)
            prop_d = MBRAT_DEF_PRIVKEY_D.copy()
            prop_d[cfg_t].update( {'name': cfgname,} )
            prop_d['pool'].update( {'name': "{}_pool".format(cfgname),} )
            args = self._mkcfg_args( cfgname, targetd, ['public',], prop_d )

        elif cfg_t == 'pubkey':
            return self._mkcfg_pubkey(cfgname, update, current)

        # now make the new config dir...
        return self._mkcfg(cfg_t, args, update, current)


    # noisy get .cfg filepaths for each current top-section configs

    def get_current_cfg(self, cfg_t, dironly=False):
        if cfg_t == 'profile':
            return self.get_current_profile_cfg(dironly)
        elif cfg_t == 'pool':
            return self.get_current_pool_cfg(dironly)
        elif cfg_t == 'poolkey':
            return self.get_current_poolkey_cfg(dironly)
        elif cfg_t == 'privkey':
            return self.get_current_data_cfg(dironly)
        elif cfg_t == 'pubkey':
            return self.get_current_pubkey_cfg(dironly)
        elif cfg_t == 'privpub':
            return self.get_current_privpub_cfg(dironly)

    def get_current_pool_cfg(self, dironly=False):
        cur_poolf = os.readlink( path.join(self.poolsd, MBRAT_CURRENTL) )
        cur_poolf = path.join( self.poolsd, cur_poolf )
        if dironly:
            return path.dirname(cur_poolf)
        return cur_poolf

    def get_current_poolkey_cfg(self, dironly=False):
        pool_datad = path.join( self.get_current_pool_cfg(dironly=True), 'data' )
        pool_datal = path.join( pool_datad, MBRAT_CURRENTL )
        if path.exists(pool_datal):
            pool_dataf = path.join( pool_datad, os.readlink(pool_datal) )
        else:
            pool_dataf = ""
        if dironly:
            return path.dirname(pool_dataf)
        return pool_dataf

    def get_current_profile_cfg(self, dironly=False):
        cur_profilef = os.readlink( path.join(self.profilesd, MBRAT_CURRENTL) )
        cur_profilef = path.join( self.profilesd, cur_profilef )
        if dironly:
            return path.dirname(cur_profilef)
        return cur_profilef

    def get_current_data_cfg(self, dironly=False):
        usr_datad = path.join( self.get_current_profile_cfg(dironly=True), 'data' )
        cur_datal = path.join( usr_datad, MBRAT_CURRENTL )
        if path.exists(cur_datal):
            dataf = path.join( usr_datad, os.readlink(cur_datal) )
        else:
            dataf = ""
        if dironly:
            return path.dirname(dataf)
        return dataf

    def get_current_pubkey_cfg(self, dironly=False):
        usr_pubd = path.join( self.get_current_profile_cfg(dironly=True), 'public' )
        cur_publ = path.join( usr_pubd, MBRAT_CURRENTL )
        if path.exists(cur_publ):
            pubkeyf = path.join( usr_pubd, os.readlink(cur_publ) )
        else:
            pubkeyf = ""
        if dironly:
            return path.dirname(pubkeyf)
        return pubkeyf

    def get_current_privpub_cfg(self, dironly=False):
        # 1st make sure there is a current pubkey set...
        cur_pubf = self.get_current_pubkey_cfg()
        if not cur_pubf:
            return cur_pubf
        # ...then return the file|dir to which it is linked
        privpubf = os.readlink(cur_pubf)
        if dironly:
            return path.dirname(privpubf)

