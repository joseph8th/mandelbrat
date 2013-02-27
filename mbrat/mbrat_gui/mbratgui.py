import os
import png
import cairo
import shutil
from os import path
from math import pi
from gi.repository import Gtk #, Gdk

from mbrat.configmgr import SecManager, ConfigManager
from mbrat.mscreen import PyMScreen
from mbrat.settings import MBRAT_GUID_GLADEF, MBRAT_TMPF, MBRAT_TMP_IMGF, MBRAT_GUI_CFGF, \
    cmap_fun
from mbrat.util import Arguments, mpoint_pick_random


class mbratgui:
    """
    The main GUI class that does all the gooey stuff for mbrat engine. 

    """

    def __init__(self):

        # MBrat ConfigManager instance
        self.cfgmgr = ConfigManager()
        self.sm = self.cfgmgr.secmgr
        self.prefs = SecManager('gui', MBRAT_GUI_CFGF)
        self._init_ui()


    # Gtk stuff and shorthand attributes follow...

    def _init_ui(self):

        # TEMPORARARY handler dict until signal & gui class method names match...
        handler_d = {
            # top-level (window and menu) signals
            "on_MainWindow_delete_event":        self.on_MainWindow_delete_event,
            "on_quitMenuitem_activate":          self.on_MainWindow_delete_event,
            "on_savePoolMenuitem_activate":      self.on_savePoolMenuitem_activate,
            "on_prefsMenuitem_activate":         self.on_prefsMenuitem_activate,
            "on_aboutMenuitem_activate":         self.on_aboutMenuitem_activate,
            # viewscreen block
            "on_mscreenNotebook_switch_page":    self.on_tab_switch,
            "on_temppoolDrawingarea_draw":       self.on_temppoolDrawingarea_draw,
            "on_pubpoolDrawingarea_draw":        self.on_pubpoolDrawingarea_draw,
            "on_privpoolDrawingarea_draw":       self.on_privpoolDrawingarea_draw,
            "on_showpointsToolbutton_toggled":   self.on_showpointsToolbutton_toggled,
            # parameter control block 
            "on_genMSetButton_clicked":          self.on_genMSetButton_pressed,
            "on_saveToPoolButton_clicked":       self.on_saveToPoolButton_clicked,
            # profile control block
            "on_profilePoolCombobox_changed":    self.on_profileCombobox_changed,
            "on_pickPoolButton_clicked":         self.on_pickPoolButton_pressed,
            "on_pickPoolKeyButton_clicked":      self.on_pickPoolKeyButton_pressed,
            "on_poolkeyPickerButton_clicked":    self.on_poolkeyPickerButton_clicked,
            "on_profileNameCombobox_changed":    self.on_profileCombobox_changed,
            "on_pickNameButton_clicked":         self.on_pickNameButton_pressed,
            "on_profilePrivKeyCombobox_changed": self.on_profileCombobox_changed,
            "on_pickPrivKeyButton_clicked":      self.on_pickPrivKeyButton_pressed,
            "on_privkeyPickerButton_clicked":    self.on_privkeyPickerButton_clicked,
            "on_addPubKeyButton_clicked":        self.on_addPubKeyButton_pressed,
            }

        self.builder = Gtk.Builder()
        self.builder.add_from_file( MBRAT_GUID_GLADEF )
        self.builder.connect_signals( handler_d )

        self.go = self.builder.get_object
        self.window = self.go("MainWindow")
        self.saveasDialog = self.go("filechooserDialog")
        self.prefsDialog = self.go("prefsDialog")
        self.aboutDialog = self.go("aboutDialog")

        self.consoleView = self.go("MSetInfoTextview")
        self.consoleBuffer = self.consoleView.get_buffer()
        self.consoleView.set_buffer(self.consoleBuffer)
        self.consoleBuffer.set_text("")
        self.consoleBuffer.insert_at_cursor(self.cfgmgr.logstr())

        self._init_image_tabs()
        self._init_comboboxes()
        self._init_state_to_prefs()
        self._set_parameterGrid_values_to_pool('tmp')

        self.window.show_all()


    # init misc UI elts to their preferred state and keep track during runtime

    def _init_state_to_prefs(self):

        pref_state = True if self.prefs.get('showpoints') == 'True' else False
        self.state = {}
        self.state['toolbar'] = { 
            'showpoints': pref_state,
            }
        elt = self.go("showpointsToolbutton").set_active(pref_state)


    # grab the DrawingAreas and init a dict to keep track of 'em & ImageSurfaces

    def _init_image_tabs(self):

        # da = DrawingArea, ims = ImageSurface
        self.tab = {
            'tmp':     { 'da': self.go("temppoolDrawingarea"), 'ims': None, },
            'pool':    { 'da': self.go("pubpoolDrawingarea"),  'ims': None, },
            'privkey': { 'da': self.go("privpoolDrawingarea"), 'ims': None, },
            }


    # read a PNG to ImageSurface obj, update (darea,surf) dict, and do queue_draw() 

    def _load_image_tab(self, cfg_t='tmp'):

        imgf = ""
        if cfg_t == 'pool':
            imgf = self.sm[cfg_t].get('image')
        elif cfg_t == 'privkey':
            imgf = self.sm[cfg_t].get_from_section('pool', 'image')
        elif cfg_t == 'tmp':
            imgf = MBRAT_TMP_IMGF

        if imgf and path.exists(imgf):
#            print imgf
            self.tab[cfg_t]['ims'] = cairo.ImageSurface.create_from_png(imgf)
            ims = self.tab[cfg_t]['ims']
            darea = self.tab[cfg_t]['da']
            darea.set_size_request( ims.get_width(), ims.get_height() )
            darea.queue_draw()


    # grab the comboboxes from the profile section to update on tab switch

    def _init_comboboxes(self):

        self.cbox = {
            'pool':    self.go("profilePoolCombobox"),
            'poolkey': self.go("profilePoolKeyCombobox"),
            'profile': self.go("profileNameCombobox"),
            'privkey': self.go("profilePrivKeyCombobox"),
            'pubkey':  self.go("profilePubKeyCombobox"),
            }
        self._load_combobox()


    # load up the config 'profile control' comboboxes using ConfigManager

    def _load_combobox(self, cfg_t=None):

        for cfg_key in self.cbox.keys():

            if not cfg_t or cfg_key in cfg_t:
                cfg_store = Gtk.ListStore(str)

                for cfg in self.cfgmgr.get_cfg_list(cfg_key):
                    cfg_store.append([cfg])

                self.cbox[cfg_key].set_model(cfg_store)


    # grab user vals from 'parameter' control & parse to args for MScreen

    def _parse_parameterGrid_values(self):

        args = Arguments()
        args.iters = int(self.go("maxiterEntry").get_text())
        args.ppu = int(self.go("ppuEntry").get_text())
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


    # set 'parameter control' fields from a dict

    def _set_parameterGrid_values(self, prop_d):

        self.go("maxiterEntry").set_text( prop_d['iters'] )
        self.go("ppuEntry").set_text( prop_d['ppu'] )
        self.go("xLoEntry").set_text( prop_d['x_lo'] )
        self.go("yLoEntry").set_text( prop_d['y_lo'] )
        self.go("xHiEntry").set_text( prop_d['x_hi'] )
        self.go("yHiEntry").set_text( prop_d['y_hi'] )

    # ... switch the above for each 'pool type' case if you will

    def _set_parameterGrid_values_to_pool(self, pool_t):

        if pool_t == 'pool':
            args = self.sm['pool'].get_as_args()
        elif pool_t == 'privkey':
            args = self.sm['privkey'].get_as_args('pool')
        elif pool_t == 'tmp':
            args = self.sm['tmp'].get_as_args('pool')

        self._set_parameterGrid_values(vars(args))


    # switch control block & 'act type' to set dependent fields sensitive

    def _set_children_sensitive(self, block, act_t):

        child_l = []
        if block == 'param':
            if act_t == 'tmp':
                child_l = [ "saveToPoolButton", ]
        elif block == 'profile':
            if act_t == 'pool':
                child_l = [ "profilePoolKeyCombobox", "pickPoolKeyButton", ]
            elif act_t == 'poolkey':
                child_l = [ "poolkeyPickerButton", ]
            elif act_t == 'profile':
                child_l = [ "profilePrivKeyCombobox", "pickPrivKeyButton", ]
            elif act_t == 'privkey':
                child_l = [ "privkeyPickerButton", 
                            "profilePubKeyCombobox", "addPubKeyButton", ]

        for child in child_l:
            self.go(child).set_sensitive(True)


    # little util method to format MScreen vars(args) for configBuffer

    def _get_ctxt_from_prop_d(self, prop_d):

        ctxt = ""
        for prop, val in prop_d.iteritems():
            ctxt += "\t{0} = {1}\n".format(prop, val)

        return ctxt


    # a general-ish method to refresh various ui elts

    def _refresh_ui(self, block=None, act_l=[]):

        pool_l = ['tmp', 'pool', 'privkey']
        act_l = pool_l if not act_l else act_l
        
        self._load_combobox()
        for act_t in act_l:
            if block:
                self._set_children_sensitive(block, act_t)
            if act_t in pool_l:
                self._load_image_tab(act_t)


    # save params from control block and img to a given pool

    def _save_param_to_pool(self, cfg_t, cfgname):

        ctxt = "==> SAVE to '{}':\n".format(cfgname)
        args = self.sm['tmp'].get_as_args('pool')
        prop_d = vars(args)

        if 'name' in prop_d.keys():
            del prop_d['name']

        if 'lims' in prop_d.keys():
            del prop_d['lims']

        # if it's bound for the current PUBLIC pool...
        if cfg_t == 'pool':
            imgf = self.sm[cfg_t].get('image')

            if not imgf:
                poold = self.sm[cfg_t].rootd
                imgf = "{}.png".format(self.sm[cfg_t].get('name'))
                imgf = path.join( poold, imgf )

            prop_d['image'] = imgf
            self.sm[cfg_t].set_write(prop_d)

        # ... or the current PRIVATE pool
        elif cfg_t == 'privkey':
            imgf = self.sm[cfg_t].get_from_section('pool', 'image')

            if not imgf:
                poold = self.sm[cfg_t].rootd
                imgf = "{}.png".format( self.sm[cfg_t].get_from_section('pool', 'name') )
                imgf = path.join( poold, imgf )

            prop_d['image'] = imgf
            self.sm[cfg_t].set_write_to_section('pool', prop_d)

        # copy tmp img to pool's dir
        shutil.copy(MBRAT_TMP_IMGF, imgf)

        if not path.exists(imgf):
            ctxt += "==> ERROR: unable to copy to '{}'".format(imgf)
        else:
            ctxt += "==> COPIED: '{}'\n-->'{}'\n".format(MBRAT_TMP_IMGF, imgf)
            ctxt += "==> CONFIGURED:\n"
            ctxt += self._get_ctxt_from_prop_d(prop_d)

            # make sure all the tabs know about this...
            self._refresh_ui( act_l=[cfg_t,] )

        return ctxt


    ##### PUBLIC HANDLERS SECTION ######################

    # handler methods for 'top-level' objects and events

    def on_MainWindow_delete_event(self, *args):
        """ Handler for every quit method """

        if self.prefs.get('savetemp') == 'False':
            if path.exists(MBRAT_TMPF):
                os.remove(MBRAT_TMPF)
        Gtk.main_quit(args)


    def on_savePoolMenuitem_activate(self, menuitem):
        """ Handler for 'Save Pool As...' menu item FileChooser Dialog. """

        response = self.saveasDialog.run()
        if response == Gtk.ResponseType.APPLY:
            imgf = self.saveasDialog.get_filename()

            shutil.copy(MBRAT_TMP_IMGF, imgf)

            if path.exists(imgf):
                ctxt = "Saved Temp Pool image to '{}'\n".format(imgf)
            else:
                ctxt = "==> ERROR: unable to save image to '{}'\n".format(imgf)

            self.consoleBuffer.insert_at_cursor(ctxt)

        self.saveasDialog.destroy()
        

    def on_prefsMenuitem_activate(self, menuitem):
        """ Handler for 'Edit Preferences' menu item Dialog. """

        savetemp_pref = self.go("prefsSavetempCheckbutton")
        savetemp_pref.set_active( self.prefs.get('savetemp') == 'True' )
        showpts_pref = self.go("prefsShowpointsCheckbutton")
        showpts_pref.set_active( self.prefs.get('showpoints') == 'True' )
        lts_pref = self.go("prefsLtsCheckbutton")
        lts_pref.set_active( self.prefs.get('lts') == 'True' )

        response = self.prefsDialog.run()
        self.prefsDialog.hide()

        if response == Gtk.ResponseType.APPLY:
            self.prefs.set_write( {
                    'savetemp': savetemp_pref.get_active(),
                    'showpoints': showpts_pref.get_active(), 
                    'lts': lts_pref.get_active(),
                    } )


    def on_aboutMenuitem_activate(self, menuitem):
        """ Handler for 'About' menu item Dialog. """

        response = self.aboutDialog.run()
        self.aboutDialog.hide()


    # handlers for DrawingArea, surface, tabs, and Toolbutton signals

    def on_tab_switch(self, notebook, page, page_num):
        """ Handler for when a Notebook Page (tab) is switched. """

        pool_l = ['tmp', 'pool', 'privkey']
        pool_t = pool_l[page_num]
        self._set_parameterGrid_values_to_pool(pool_t)


    def on_draw(self, pool_t, darea, cr):
        """ Draw method for any given DrawingArea and target tab ('pool type'). """

        cr.set_source_surface( self.tab[pool_t]['ims'], 0, 0 )
        cr.paint()
        
    # handlers for 'on_draw' cases for each tab...

    def on_temppoolDrawingarea_draw(self, darea, cr):
        self.tab['tmp']['da'] = darea
        if self.tab['tmp']['ims']:
            self.on_draw('tmp', darea, cr)


    def on_pubpoolDrawingarea_draw(self, darea, cr):
        self.tab['pool']['da'] = darea
        if self.tab['pool']['ims']:

            if self.state['toolbar']['showpoints']:
                self._draw_layer_in_tab('pool')

            self.on_draw('pool', darea, cr)


    def on_privpoolDrawingarea_draw(self, darea, cr):
        self.tab['privkey']['da'] = darea
        if self.tab['privkey']['ims']:

            if self.state['toolbar']['showpoints']:
                self._draw_layer_in_tab('privkey')

            self.on_draw('privkey', darea, cr)


    def on_showpointsToolbutton_toggled(self, button):
        """ Handler for the 'show points' Toolbutton. """

        self.state['toolbar']['showpoints'] = button.get_active()
        self._refresh_ui( act_l=['tmp', 'pool', 'privkey'] )


    # handlers for the 'parameter control block'

    def on_genMSetButton_pressed(self, button):
        """ Method for when 'Generate Mandelbrot Set' button is pressed. """

        args = self._parse_parameterGrid_values()
        # new MScreen from ui param block
        self.mscreen = PyMScreen(args)
        self.mscreen.gen_mscreen()
        self.mscreen.gen_mset()
        ctxt = "{}\n".format(self.mscreen.get_info())

        # make png from mscreen and save to tmp
        img = self.mscreen.get_img()
        png_img = png.from_array( img, 'L' )
        png_img.save( MBRAT_TMP_IMGF )

        # update the SecManager
        del args.lims
        self.sm['tmp'].set_write_to_section('pool', vars(args))

        # load it up...
        self._refresh_ui( block='param', act_l=['tmp',])

        self.consoleBuffer.insert_at_cursor( ctxt )


    def on_saveToPoolButton_clicked(self, button):
        """ Copies the tmp .cfg and .png file into the chosen pool configd. """

        pool_txt = self.go("saveToPoolCombobox").get_active_text()
        ctxt = "Saving Mandelbrot set to current {} ...\n".format(pool_txt)
        cfg_t = 'pool' if 'Public' in pool_txt else 'privkey'
        cfg_iter = self.cbox[cfg_t].get_active_iter()

        if not cfg_iter:
            cfgname = self.cbox[cfg_t].get_child().get_text()
        else:
            model = self.cbox[cfg_t].get_model()
            cfgname = model[cfg_iter][0]

        if not cfgname:
            ctxt += "==> ERROR: activate an existing pool first\n"
        else:
            if not cfgname in self.cfgmgr.get_cfg_list(cfg_t):
                ctxt += "==> ERROR: {0} '{1}' not found\n".format(cfg_t, cfgname)
            else:
                ctxt += self._save_param_to_pool(cfg_t, cfgname)

        self._refresh_ui( act_l=[cfg_t,] )
        self.consoleBuffer.insert_at_cursor(ctxt)


    # handler methods for profile control block

    def on_pickConfigButton(self, cfg_t, button):
        """ Generic handler for the APPLY buttons next to Comboboxes. """

        ctxt = ""
        cfg_iter = self.cbox[cfg_t].get_active_iter()

        if cfg_iter != None:
            model = self.cbox[cfg_t].get_model()
            cfgname = model[cfg_iter][0]
        else:
            cfgname = self.cbox[cfg_t].get_child().get_text()

            if cfgname == "":
                ctxt += "C'mon now! Ya gotta type in a name.\n"
                self.consoleBuffer.insert_at_cursor(ctxt)
                return

            if cfgname not in self.cfgmgr.get_cfg_list(cfg_t):
                ctxt += "Making new {0} '{1}' ...\n".format(cfg_t, cfgname)

                if not self.cfgmgr.make_config( cfg_t, cfgname ):
                    ctxt += self.cfgmgr.errstr()
                    self.consoleBuffer.insert_at_cursor(ctxt)
                    return

                self.sm[cfg_t].set_configf_by_name(cfgname)
                self._load_combobox(cfg_t=cfg_t)

        ctxt += "Activating {0} '{1}' ... ".format(cfg_t, cfgname)

        if self.cfgmgr.set_current_cfg_by_name(cfg_t, cfgname):
            self.sm[cfg_t].set_configf_by_name(cfgname)
            self.sm[cfg_t].read()
            ctxt += "{0} '{1}' activated.\n".format(cfg_t, cfgname)
            ctxt += "==> INFO: {}\n".format( self.sm[cfg_t].get('info') )
            self._refresh_ui( block='profile', act_l=[cfg_t,] )
        else:
            ctxt += "\n==> ERROR: could not activate {0} '{1}'\n".format(cfg_t, cfgname)

        self.consoleBuffer.insert_at_cursor(ctxt)


    # dummy handlers redirect to pickConfigButton...

    def on_pickPoolButton_pressed(self, button):
        self.on_pickConfigButton( 'pool', button )

    def on_pickPoolKeyButton_pressed(self, button):
        self.on_pickConfigButton( 'poolkey', button )

    def on_pickNameButton_pressed(self, button):
        self.on_pickConfigButton( 'profile', button )

    def on_pickPrivKeyButton_pressed(self, button):
        self.on_pickConfigButton( 'privkey', button )

    def on_addPubKeyButton_pressed(self, button):
        self.on_pickConfigButton( 'pubkey', button )


    # handlers for when 'parent' comboboxes are changed...

    def on_profileCombobox_changed(self, widget):
        self._refresh_ui()


    # RANDOM point-picker handlers rely on extern method...

    def on_poolkeyPickerButton_clicked(self, button):
        """ Pick a RANDOM key-point from the PUBLIC pool. """

        result = mpoint_pick_random( self.cfgmgr, 'poolkey', self.prefs.get('lts') )
        ctxt = result.log if not result.err else result.err
        
        self._refresh_ui( act_l=['pool'] )
        self.consoleBuffer.insert_at_cursor(ctxt)

        print result.mpoint.Get_ix(), " ", result.mpoint.Get_iy()

        
    def on_privkeyPickerButton_clicked(self, button):
        """ Pick a RANDOM key-point from the PRIVATE pool. """

        result = mpoint_pick_random(self.cfgmgr, 'privkey', self.prefs.get('lts') )
        ctxt = result.log if not result.err else result.err

        self._refresh_ui( act_l=['privkey'] )
        self.consoleBuffer.insert_at_cursor(ctxt)

        print result.mpoint.Get_ix(), " ", result.mpoint.Get_iy()


    # Additional draw methods

    def _draw_layer_in_tab(self, pool_t):
        """ Draws on ImageSurface using Cairo derived Context. """

        if pool_t in ['pool', 'privkey']:
            ppu = int( self.sm[pool_t].get_from_section('pool', 'ppu') )
            x_lo = float( self.sm[pool_t].get_from_section('pool', 'x_lo') )
            y_hi = float( self.sm[pool_t].get_from_section('pool', 'y_hi') )

            key_cfg = self.sm['poolkey'] if pool_t == 'pool' else self.sm['privkey']
            self.sm[pool_t].reset_section()
            
            x = float( key_cfg.get('real') )
            y = float( key_cfg.get('imag') )
        
            ix = ppu*(x - x_lo) - 0.5
            iy = 0.5 - ppu*(y - y_hi)

#            print ix, " ", iy
            self._draw_point(pool_t, (ix, iy), 5)


    def _draw_point(self, pool_t, ptix, pxrad):
        
        cr = cairo.Context( self.tab[pool_t]['ims'] )

        cr.set_source_rgb(1.0, 0.0, 0.0)
        cr.translate(ptix[0], ptix[1])
        cr.arc(0, 0, pxrad, 0, 2*pi)
#        cr.rectangle(ptix[0], ptix[1], pxrad, pxrad)
        cr.fill()
