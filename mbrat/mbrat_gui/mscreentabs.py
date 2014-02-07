import png
import cairo
from math import pi
from gi.repository import Gtk

from mbrat.util import Arguments, clogger
from mbrat.mutil import mpoint_pick_random
from mbrat.settings import MBRAT_GUI_POOL_TYPE_L as POOL_TYPE_L

POOL_TYPES = { 
    'tmp': { 'tabn': "Temp Pool", }, 
    'pool': { 'tabn': "Public Pool", }, 
    'privkey': { 'tabn': "Private Pool", },
    }


class MScreenTabs(object):
    """ 
    A class to manage Gtk.DrawingAreas inside Gtk.Notebook pages. 

    """

    def __init__(self, builder):
        self.builder = builder
        self._init_tabs()


    def _init_tabs(self):

        from mbrat.lib.mscreen import PyMScreen

        self.tab = POOL_TYPES

        for pool_t in POOL_TYPES.keys():
            # init empty image surface entries...
            self.tab[pool_t]['ims'] = None

            # set MScreen for the tab...
            self.tab[pool_t]['mset'] = PyMScreen()

            # init DAreas...
            self.tab[pool_t]['da'] = self.builder.get_object(
                "{}Drawingarea".format(pool_t)
                )


    # accessors & mutators

    def set_state_callback(self, state_callback):
        self.state = state_callback


    # public methods

    def load_image_tab(self, pool_t):

        sm = self.state(pool_t)
        imgf = sm.get_from_section('pool', 'image')

        if imgf:
            self.tab[pool_t]['ims'] = cairo.ImageSurface.create_from_png(imgf)
            ims = self.tab[pool_t]['ims']
            self.tab[pool_t]['da'].set_size_request( ims.get_width(), ims.get_height() )
            self.tab[pool_t]['da'].queue_draw()


    def gen_mset_to_png(self, pool_t, args):

        ms = self.tab[pool_t]['mset']
        ms.set_params(args)
        ms.gen_mscreen()
        ms.gen_mset()

        # make png from mscreen and save to tmp
        png_img = png.from_array( ms.get_img(), 'L' )
        png_img.save( args.image )

        return clogger( ms.get_info() )


    def pick_mpoint(self, pick_t, key_t, cfgmgr, lts=False):

        pool_t = 'pool' if 'pool' in key_t else key_t

        if pick_t == 'random':
            result = mpoint_pick_random(cfgmgr, key_t, lts)
            self.tab[pool_t]['da'].queue_draw()
            return result
    

    # handlers for DrawingArea, surface, tabs, and Toolbutton signals

    def on_draw(self, pool_t, cr):
        """ Draw method for any given DrawingArea and target tab ('pool type'). """

        cr.set_source_surface( self.tab[pool_t]['ims'], 0, 0 )
        cr.paint()
        
    # handlers for 'on_draw' cases for each tab...

    def on_tmpTab_draw(self, darea, cr):
        self.tab['tmp']['da'] = darea
        if self.tab['tmp']['ims']:
            self.on_draw('tmp', cr)


    def on_poolTab_draw(self, darea, cr):
        self.tab['pool']['da'] = darea
        if self.tab['pool']['ims']:

            if self.state('showpoints'):
                self._draw_layer_in_tab('pool')

            self.on_draw('pool', cr)


    def on_privkeyTab_draw(self, darea, cr):
        self.tab['privkey']['da'] = darea
        if self.tab['privkey']['ims']:

            if self.state('showpoints'):
                self._draw_layer_in_tab('privkey')

            self.on_draw('privkey', cr)


    # Additional draw methods

    def _draw_layer_in_tab(self, pool_t):
        """ Draws on ImageSurface using Cairo derived Context. """

###########33        print pool_t
#        sm = self.state(pool_t)

        key_t = 'poolkey' if pool_t == 'pool' else pool_t            
        key_cfg = self.state(key_t)
            
#        sm.reset_section()

        # if key point exists then draw it...
        ix = key_cfg.get_from_section(key_t, 'ix')
        iy = key_cfg.get_from_section(key_t, 'iy')

########3333333        print (ix, iy)

        if ix and iy:
            ix = float( ix )
            iy = float( iy )
            self._draw_point(pool_t, (ix, iy), 5)


    def _draw_point(self, pool_t, ptix, pxrad):
        
#######33333        print ptix

        cr = cairo.Context( self.tab[pool_t]['ims'] )

        cr.set_source_rgb(1.0, 0.0, 0.0)
        cr.translate(ptix[0], ptix[1])
        cr.arc(0, 0, pxrad, 0, 2*pi)
        cr.fill()
