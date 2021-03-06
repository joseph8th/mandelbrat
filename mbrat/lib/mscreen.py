import png
import random
import gmpy2
from gmpy2 import mpc, mpfr, add

from os import path
#from bigfloat import BigFloat, add, sub, div, floor, precision

from mbrat.settings import cmap_fun, MBRAT_DEF_PRECISION
from mbrat.lib.mpoint import MPoint


class PyMScreen(object):
    """
    Class to encapsulate set-rendering matrix, handle mpoint objects,
    and generate image objects to spec.

    """

    def __init__(self, args=None):
        if args != None:
            self._init_from(args)
 

    def _init_from(self, args):
#        from mbrat.util import Arguments

        # 1st set the precision ...
        if not hasattr(args, 'prec'):
            args.prec = MBRAT_DEF_PRECISION
        self.prec = int(args.prec)

        gmpy2.get_context().precision = self.prec

        # ... make sure lims dict is right ...
        if not hasattr(args, 'lims'):
            self.limits = { 'low': mpc(mpfr(args.x_lo), mpfr(args.y_lo)),
                            'high': mpc(mpfr(args.x_hi), mpfr(args.y_hi)), }
        else:
            self.limits = args.lims

        # ... init the core stuff ...
        self._init_new(args)

        # ... if 'ini_d' dict provided then init more depending...
        if hasattr(args, 'ini_d'):
            if 'image' in args.ini_d:
                self.gen_mscreen_from_img( args.ini_d['image'] )


    def _init_new(self, args):

        l = self.limits
        self.ppu = int(args.ppu)
        self.width = l['high'].real - l['low'].real
        self.height = l['high'].imag - l['low'].imag
        self.px_width = int(self.width * self.ppu)
        self.px_height = int(self.height * self.ppu)
        self.iters = int(args.iters)
        self.cmap = cmap_fun(args.cmap)
        self.screen = None


    def set_params(self, args):
        self._init_from(args)


    # primary generators

    def gen_mscreen(self):
        """
        Generate a set-rendering matrix set to the current instance properties. """

#        with precision(self.prec):
        d = float(1.0/self.ppu)
        rows = []
        for iy in range(self.px_height):
            rows.append([])
            for ix in range(self.px_width):
                x = self.limits['low'].real + d*(0.5 + ix)
                y = self.limits['high'].imag - d*(0.5 + iy)
                rows[iy].append( MPoint(mpc(x, y), self.prec) )
                rows[iy][ix].Set_Index(ix, iy)

        self.screen = rows


    def gen_mset(self):
        """ Generate a Mandelbrot set with the current screen settings. """

        for row in self.screen:
            for pt in row:
                pt.Run_MFun(self.iters, complex(0.0, 0.0))


    def gen_mscreen_from_img(self, imgf):
        # first read and verify image data and metadata
        rdr = png.Reader(imgf)
        pxw, pxh, img, meta = rdr.read()
        if pxw != self.px_width or pxh != self.px_height:
            raise RuntimeError("image file and config file do not match")
        img_l = list(img)

        # gen an MScreen and set inmset flag on MPoints corresp. to image px
        self.gen_mscreen()
        for iy in range(self.px_height):
            img_row = list( img_l[iy] ) 
            ms_row = self.screen[iy]
            for ix in range(self.px_width):
                if not img_row[ix]:
                    ms_row[ix].inmset = True


    # accessors/mutators/generators

    def get_img(self):
        img = []
        for iy in range(len(self.screen)):
            img.append([])
            for pt in self.screen[iy]:
                img[iy].append( self.cmap(pt.iters, self.iters) )
        return img


    def get_png(self):
        self.gen_mscreen()
        self.gen_mset()
        return png.from_array( self.get_img(), 'L' )


    def gen_to_file(self, args):
        png_img = self.get_png()
        png_img.save(args)


    def get_inmset(self):
        inmset_l = []
        for row in self.screen:
            inmset_l.extend( [pt for pt in row if pt.inmset] )
        return inmset_l
    

    def get_mpoint(self):
        random.seed()
        inmset_l = self.get_inmset()
        randix = random.randint(0, len(inmset_l)-1)
        return inmset_l[randix]


    def get_info(self):
        ms_info = "MBrat Screen Settings:\n"
        ms_info += "\tprecision = {} bits\n".format(self.prec)
        ms_info += "\tlimits: [z_lo, z_hi] = [ "
        ms_info += "({0.real:.3}, {0.imag:.3}), ".format(self.limits['low'])
        ms_info += "({0.real:.3}, {0.imag:.3}) ]\n".format(self.limits['high'])
        ms_info += "\tunit size: (w,h) = (%.3f, %.3f)\n" % (self.width, self.height)
        ms_info += "\tresolution (pixels per unit) = %d\n" % self.ppu
        ms_info += "\tpixel size: (w,h) = (%d, %d)\n" % (self.px_width, self.px_height)
        ms_info += "\tmax. iterations = %d" % self.iters
        return ms_info
