import os
import png
import cairo
import shutil
from os import path
from math import pi
from gi.repository import Gtk #, Gdk

from mbrat.configmgr import SecManager, ConfigManager
from mbrat.lib.mscreen import PyMScreen
from mbrat.settings import MBRAT_VER, MBRAT_TMPF, MBRAT_TMP_IMGF, MBRAT_CFG_TYPE_L, \
    MBRAT_CFG_DEPTREE_D, MBRAT_GUID_GLADEF, MBRAT_USR_CFGF, MBRAT_GUI_DEPTREE_D, \
    MBRAT_DEF_MPBACKEND, cmap_fun
from mbrat.util import Arguments, clogger
from mbrat.mbrat_gui.mscreentabs import POOL_TYPE_L, MScreenTabs


class mbratgui:
    """
    The main GUI class that does all the gooey stuff for mbrat engine. 

    """

    def __init__(self):

        # MBrat ConfigManager instance
        self.cfgmgr = ConfigManager()
        self.sm = self.cfgmgr.secmgr
        self.prefs = SecManager('prefs', MBRAT_USR_CFGF)
        self._init_ui()


    # Gtk stuff and shorthand attributes follow...

    def _init_ui(self):

        # g/set & connect the Builder, & shortcut 'get_object' method ...
        self.builder = Gtk.Builder()
        self.builder.add_from_file( MBRAT_GUID_GLADEF )
        self.builder.connect_signals( self )

        self.go = self.builder.get_object

        # ... g/set the windows incl Dialogs ... 
        self.window = self.go("MainWindow")
        self.saveasDialog = self.go("fileSaveDialog")
        self.prefsDialog = self.go("prefsDialog")
        self.aboutDialog = self.go("aboutDialog")
        self.errorDialog = self.go("errorDialog")

        # ... g/set & init the console Textview ...
        self.consoleView = self.go("MSetInfoTextview")
        self.consoleBuffer = self.consoleView.get_buffer()
        self.consoleView.set_buffer(self.consoleBuffer)
        self.consoleBuffer.set_text("")
        self.consoleBuffer.insert_at_cursor(self.cfgmgr.logstr())

        # ... g/set & init the profile block elts (Combobox, etc) ...
        self._init_profileControl()

        # ... init a state dict from prefs configf & current cfgmgr ...
        self._init_state()

        # ... instantiate & init the Notebook manager ...
        self.tabs = MScreenTabs(self.builder)
        self.tabs.set_state_callback(self._state)

        # ... g/set & init the param block elts (Entry, etc) ...
        self._set_parameterGrid_values_to_pool('tmp')

        # ... init state-dependent ui elts to initial state (forces redraw) ...
        self._init_ui_to_state()

        # ... show_off_my_fancy_gui()
        self.window.show_all()


    # grab the comboboxes from the profile section to update on tab switch

    def _init_profileControl(self):

        self.cbox = {
            'pool':    self.go("profilePoolCombobox"),
            'poolkey': self.go("profilePoolKeyCombobox"),
            'profile': self.go("profileNameCombobox"),
            'privkey': self.go("profilePrivKeyCombobox"),
            'pubkey':  self.go("profilePubKeyCombobox"),
            }


    # init a state dict and set vals to preferred or current states

    def _init_state(self):

        self.state = {}

        # init state properties from prefs configf ...
        showpoints_state = True if self.prefs.get('showpoints') == 'True' else False
        lts_state = True if self.prefs.get('lts') == 'True' else False
        self.state.update( { 'showpoints': showpoints_state,
                             'lts': lts_state, } )

        # ... init state props from current ConfigManager state
        for cfg_t in self.sm.keys():
            self.state[cfg_t] = self.sm[cfg_t]


    # state mutator & callback method

    def _state(self, key, value=None):

        # setter routine 
        if value != None:
            self.state[key] = value
        # getter routine
        else:
            return self.state[key]

    # init misc UI elts to state

    def _init_ui_to_state(self):

        self.go("showpointsToolbutton").set_active( 
                self._state('showpoints') 
                )
        self._load_combobox()


    # switch 'control block type' & 'act type' to set dependent fields (in)sensitive

    def _set_children_sensitive(self, block, act_t, sensitive=True):

        cascade_l = [act_t,]
        if not sensitive and block == 'profile':
            if act_t == 'pool':
                cascade_l.append( 'poolkey' )
            elif act_t == 'profile':
                cascade_l.append( 'privkey' )

        for act in cascade_l:
            child_l = MBRAT_GUI_DEPTREE_D[block][act]

            for child in child_l:
                cbox = self.go(child)
                if cbox.get_sensitive() != sensitive:
                    cbox.set_sensitive(sensitive)


    # load up the config 'profile control' block comboboxes using ConfigManager

    def _load_combobox(self, cfg_t=None):

        for cfg_key in MBRAT_CFG_TYPE_L:
            if not cfg_t or cfg_key in cfg_t:

                # get the current cfg name and cfg list for this cfg_key
                cur_cfg = self._state(cfg_key)
                cur_cfg.reset_section()
                cur_cfgn = cur_cfg.get('name')
                if cur_cfgn != None:
                    cur_cfgn = "{}.cfg".format(cur_cfgn) if cfg_key == 'pubkey' else cur_cfgn
                cfg_l = self.cfgmgr.get_cfg_list(cfg_key)

                # create the list model for the combobox
                cfg_store = Gtk.ListStore(str)
                for cfg in cfg_l:
                    cfg_store.append([cfg])

                # set/replace combobox's model with the ListStore
                self.cbox[cfg_key].set_model(cfg_store)
                if cur_cfgn != None:
                    self.cbox[cfg_key].set_active( cfg_l.index(cur_cfgn) )


    # read a PNG to ImageSurface obj, update (darea,surf) dict, and do queue_draw() 

    def _load_image_tab(self, pool_t='tmp'):
        self.tabs.load_image_tab(pool_t)


    # a general-ish method to refresh various ui elts

    def _refresh_ui(self, block=None, act_l=[]):

        act_l = POOL_TYPE_L if not act_l else act_l

        for act_t in act_l:
            if block:
                self._set_children_sensitive(block, act_t, sensitive=True)
            if act_t in POOL_TYPE_L:
                self._load_image_tab(act_t)

        self._load_combobox()


    # grab user vals from 'parameter' control block & parse to args for MScreen

    def _parse_parameterGrid_values(self):

        args = Arguments()
        args.iters = int(self.go("maxiterEntry").get_text())
        args.ppu = int(self.go("ppuEntry").get_text())
        args.prec = int(self.go("precEntry").get_text())
        x_lo = args.x_lo = self.go("xLoEntry").get_text()    
        y_lo = args.y_lo = self.go("yLoEntry").get_text()    
        x_hi = args.x_hi = self.go("xHiEntry").get_text()    
        y_hi = args.y_hi = self.go("yHiEntry").get_text()
        args.lims = { 'low':complex( float(x_lo), float(y_lo) ), 
                      'high':complex( float(x_hi), float(y_hi) ) }
        c = self.go("cmapComboboxtext").get_active_text()

        if c and "Grayscale" in c:
            args.cmap = 'grey'
        else:
            args.cmap = 'bw'

        return args


    # set 'parameter control' block fields from a dict

    def _set_parameterGrid_values(self, prop_d):

        self.go("maxiterEntry").set_text( prop_d['iters'] )
        self.go("ppuEntry").set_text( prop_d['ppu'] )
        self.go("xLoEntry").set_text( prop_d['x_lo'] )
        self.go("yLoEntry").set_text( prop_d['y_lo'] )
        self.go("xHiEntry").set_text( prop_d['x_hi'] )
        self.go("yHiEntry").set_text( prop_d['y_hi'] )


    def _set_parameterGrid_values_to_pool(self, pool_t):

        if pool_t in POOL_TYPE_L:
            sm = self._state(pool_t)
            args = sm.get_as_args() if pool_t == 'pool' else sm.get_as_args('pool')
            self._set_parameterGrid_values(vars(args))


    # little util method to format MScreen vars(args) for configBuffer

    def _get_ctxt_from_prop_d(self, prop_d):

        ctxt = ""
        for prop, val in prop_d.iteritems():
            ctxt += "\t{0} = {1}\n".format(prop, val)
        return ctxt


    ##### PUBLIC HANDLERS SECTION ######################

    # handlers for DrawingArea, surface, tabs, and Toolbutton signals

    def on_mscreenNotebook_switch_page(self, notebook, page, page_num):
        """ Handler for when a Notebook Page (tab) is switched. """

        pool_t = POOL_TYPE_L[page_num]
        self._set_parameterGrid_values_to_pool(pool_t)


    def on_showpointsToolbutton_toggled(self, button):
        """ Handler for the 'show points' Toolbutton. """

        self._state( 'showpoints', button.get_active() )
        self._refresh_ui()

        
    # handlers for 'on_draw' cases for each tab...

    def on_tmpDrawingarea_draw(self, darea, cr):
        self.tabs.on_tmpTab_draw(darea, cr)

    def on_poolDrawingarea_draw(self, darea, cr):
        self.tabs.on_poolTab_draw(darea, cr)

    def on_privkeyDrawingarea_draw(self, darea, cr):
        self.tabs.on_privkeyTab_draw(darea, cr)


    # handlers for the 'parameter control block'

    def on_genMSetButton_clicked(self, button):
        """ Method for when 'Generate Mandelbrot Set' button is pressed. """

        args = self._parse_parameterGrid_values()
        args.image = MBRAT_TMP_IMGF

        # generate the mset to png temp file
        ctxt = self.tabs.gen_mset_to_png('tmp', args)
        ctxt = clogger(ctxt, lts=self._state('lts'))

        # update the SecManager
        del args.lims

        self.sm['tmp'].set_write_to_section('pool', vars(args))

        # load it up...
        self._refresh_ui( block='param', act_l=['tmp',])

        if ctxt:
            self.consoleBuffer.insert_at_cursor( "{}\n".format(ctxt) )


    # 'private' method to save params from control block and img to a given pool

    def _save_param_to_pool(self, cfg_t, cfgname):

        ctxt = clogger("==> SAVE to '{}':\n".format(cfgname), 
                       lts=self._state('lts'))

        tmp_sm = self._state('tmp')
        prop_d = vars( tmp_sm.get_as_args('pool') )

        if 'name' in prop_d.keys():
            del prop_d['name']

        if 'lims' in prop_d.keys():
            del prop_d['lims']

        if cfg_t in ['pool', 'privkey']:
            sm = self._state(cfg_t)
            imgf = sm.get_from_section('pool', 'image')

            if not imgf:
                poold = sm.rootd
                imgf = "{}.png".format(sm.get_from_section('pool', 'name'))
                imgf = path.join( poold, imgf )

            prop_d['image'] = imgf
            sm.set_write_to_section('pool', prop_d)

        # copy tmp img to pool's dir
        shutil.copy(MBRAT_TMP_IMGF, imgf)

        if not path.exists(imgf):
            ctxt += clogger("==> ERROR: unable to copy to '{}'".format(imgf),
                            lts=self._state('lts'), err=True)
        else:
            ctxt += clogger(
                "==> COPIED: '{0}'\n-->'{1}'\n==> CONFIGURED:\n{2}".format(
                    MBRAT_TMP_IMGF, imgf, self._get_ctxt_from_prop_d(prop_d)
                    ),
                lts=self._state('lts')
                )

            # make sure all the tabs know about this...
            self._refresh_ui( act_l=[cfg_t,] )

        return ctxt


    def on_saveToPoolButton_clicked(self, button):
        """ Copies the tmp .cfg and .png file into the chosen pool configd. """

        pool_txt = self.go("saveToPoolCombobox").get_active_text()

        cfg_t = 'pool' if 'Public' in pool_txt else 'privkey'
        cfg_iter = self.cbox[cfg_t].get_active_iter()

        cfgerr = False
        if not cfg_iter:
            cfgname = self.cbox[cfg_t].get_child().get_text()
        else:
            model = self.cbox[cfg_t].get_model()
            cfgname = model[cfg_iter][0]

        if not cfgname:
            cfgerr = True
            ctxt = clogger("==> ERROR: activate an existing pool first\n",
                           lts=self._state('lts'), err=cfgerr)
        else:
            if not cfgname in self.cfgmgr.get_cfg_list(cfg_t):
                cfgerr = True
                ctxt = clogger("==> ERROR: {0} '{1}' not found\n".format(cfg_t, cfgname),
                               lts=self._state('lts'), err=cfgerr)
            else:
                ctxt = clogger("Saving Mandelbrot set to current {0} ...\n".format(pool_txt),
                               lts=self._state('lts'))

                # everything set? then save (copy) from 'tmp' to chosen pool...
                ctxt += self._save_param_to_pool(cfg_t, cfgname)

        if ctxt:
            self.consoleBuffer.insert_at_cursor("{}\n".format(ctxt))

        if not cfgerr:
            self._refresh_ui( act_l=[cfg_t,] )


    # handler methods for profile control block

    def on_pickConfigButton(self, cfg_t, button):
        """ Generic handler for the APPLY buttons next to Comboboxes. """

        ctxt = ""
        cfg_iter = self.cbox[cfg_t].get_active_iter()

        # cfg_iter points to user choice? ...
        if cfg_iter != None:
            model = self.cbox[cfg_t].get_model()
            cfgname = model[cfg_iter][0]

        # ... or to an Entry?
        else:
            cfgname = self.cbox[cfg_t].get_child().get_text()

            if cfgname == "":
                ctxt = clogger("C'mon now! Ya gotta type in a name.\n",
                                lts=self._state('lts'), err=True)
                if ctxt:
                    self.consoleBuffer.insert_at_cursor("{}\n".format(ctxt))
                return

            # are we making a new config?
            if cfgname not in self.cfgmgr.get_cfg_list(cfg_t):
                ctxt = clogger("Making new {0} '{1}' ...\n".format(cfg_t, cfgname),
                               lts=self._state('lts'))

                if not self.cfgmgr.make_config( cfg_t, cfgname ):
                    ctxt += clogger(self.cfgmgr.errstr(),
                                    lts=self._state('lts'), err=True)
                    if ctxt:
                        self.consoleBuffer.insert_at_cursor(ctxt)
                    return

                self.sm[cfg_t].set_configf_by_name(cfgname)
                self._load_combobox(cfg_t=cfg_t)

        ctxt += clogger("==> Activating {0} '{1}' ... \n".format(cfg_t, cfgname),
                        lts=self._state('lts'))

        # update ConfigManager and cfg state
        if self.cfgmgr.set_current_cfg_by_name(cfg_t, cfgname):
            ctxt += clogger(
                "  -> {0} '{1}' activated\n  -> Info: {2}\n".format(
                    cfg_t, cfgname, self.sm[cfg_t].get('info')
                    ), 
                lts=self._state('lts') 
                )
        else:
            ctxt += clogger("==> ERROR: could not activate {0} '{1}'\n".format(cfg_t, cfgname),
                            lts=self._state('lts'), err=True)

        if ctxt:
            self.consoleBuffer.insert_at_cursor(ctxt)

        self._refresh_ui( block='profile', act_l=[cfg_t,] )


    # dummy handlers redirect to pickConfigButton...

    def on_pickPoolButton_clicked(self, button):
        self.on_pickConfigButton( 'pool', button )

    def on_pickPoolKeyButton_clicked(self, button):
        self.on_pickConfigButton( 'poolkey', button )

    def on_pickNameButton_clicked(self, button):
        self.on_pickConfigButton( 'profile', button )

    def on_pickPrivKeyButton_clicked(self, button):
        self.on_pickConfigButton( 'privkey', button )

    def on_addPubKeyButton_clicked(self, button):
        self.on_pickConfigButton( 'pubkey', button )


    # handler stubs for when 'parent' comboboxes are changed (pass for now)...

    def on_profilePoolCombobox_changed(self, widget):
        pass

    def on_profileNameCombobox_changed(self, widget):
        pass

    def on_profilePrivKeyCombobox_changed(self, widget):
        pass


    # RANDOM point-picker handlers rely on extern method...

    def on_pointPickerButton(self, key_t, button):
        """ Pick a RANDOM key-point from the appropriate pool. """

        result = self.tabs.pick_mpoint( 'random', key_t, self.cfgmgr, 
                                        lts=self._state('lts') )

        if not result.err:
            ctxt = clogger(result.log, lts=self._state('lts'))
        else:
            ctxt = clogger(result.err, lts=self._state('lts'), err=True)        

        if ctxt:
            self.consoleBuffer.insert_at_cursor(ctxt)

        self._refresh_ui()


    def on_poolkeyPickerButton_clicked(self, button):
        self.on_pointPickerButton('poolkey', button)
        
    def on_privkeyPickerButton_clicked(self, button):
        self.on_pointPickerButton('privkey', button)


    # handler methods for 'top-level' menus, dialogs and events

    def on_MainWindow_delete_event(self, *args):
        """ Handler for every quit method """

        if self.prefs.get('savetemp') == 'False':
            if path.exists(MBRAT_TMPF):
                os.remove(MBRAT_TMPF)
        Gtk.main_quit(args)


    def on_quitMenuitem_activate(self, menuitem):
        self.on_MainWindow_delete_event()


    def on_savePoolMenuitem_activate(self, menuitem):
        """ Handler for 'Save Pool As...' menu item FileChooser Dialog. """

        response = self.saveasDialog.run()
        if response == Gtk.ResponseType.APPLY:
            imgf = self.saveasDialog.get_filename()

            shutil.copy(MBRAT_TMP_IMGF, imgf)

            if path.exists(imgf):
                ctxt = clogger("Saved Temp Pool image to '{}'\n".format(imgf),
                               lts=self._state('lts'))
            else:
                ctxt = clogger("==> ERROR: unable to save image to '{}'\n".format(imgf),
                               lts=self._state('lts'), err=True)

            if ctxt:
                self.consoleBuffer.insert_at_cursor("{}\n".format(ctxt))

        self.saveasDialog.destroy()
        

    def on_prefsMenuitem_activate(self, menuitem):
        """ Handler for 'Edit Preferences' menu item Dialog. """

        # save temp pool config between sessions?
        savetemp_pref = self.go("prefsSavetempCheckbutton")
        savetemp_pref.set_active( self.prefs.get('savetemp') == 'True' )
        # show all key-points in pool image views by default?
        showpts_pref = self.go("prefsShowpointsCheckbutton")
        showpts_pref.set_active( self.prefs.get('showpoints') == 'True' )
        # log to terminal stdout instead of gui console?
        lts_pref = self.go("prefsLtsCheckbutton")
        lts_pref.set_active( self.prefs.get('lts') == 'True' )

        response = self.prefsDialog.run()
        self.prefsDialog.hide()

        if response == Gtk.ResponseType.APPLY:
            # multiprecision python backend (mpmath or BigFloat) to use
            mpbe_pref = self.go("prefsMPBackendCombobox").get_active_text()
            mpbe_pref = MBRAT_DEF_MPBACKEND if mpbe_pref == None else mpbe_pref 
            
            # write prefs to usr.cfg
            self.prefs.set_write( {
                    'savetemp': savetemp_pref.get_active(),
                    'showpoints': showpts_pref.get_active(), 
                    'lts': lts_pref.get_active(),
                    'mpbackend': mpbe_pref,
                    } )


    def on_aboutMenuitem_activate(self, menuitem):
        """ Handler for 'About' menu item Dialog. """

        self.aboutDialog.set_version(MBRAT_VER)
        response = self.aboutDialog.run()
        self.aboutDialog.hide()


    def _errorDialog(self, errstr):
        """ Method for runtime error MessageDialog. """

        self.errorDialog.format_secondary_text(errstr)
        self.errorDialog.run()
        self.errorDialog.destroy()
