from mbrat.settings import cmap_fun
from mpoint import MPoint

class PyMScreen(object):

    def __init__(self, args):
        self.ppu = args.ppu
        l = self.limits = args.lims
        self.width = l['high'].real - l['low'].real
        self.height = l['high'].imag - l['low'].imag
        self.px_width = int(self.width * self.ppu)
        self.px_height = int(self.height * self.ppu)
        self.iters = args.iters
        self.cmap = cmap_fun(args.cmap)
        self.screen = None

    def get_info(self):
        ms_info = "MBrat Screen Settings:\n"
        ms_info += "\tlimits: [z_lo, z_hi] = [ "
        ms_info += "({0.real:.3}, {0.imag:.3}), ".format(self.limits['low'])
        ms_info += "({0.real:.3}, {0.imag:.3}) ]\n".format(self.limits['high'])
        ms_info += "\tunit size: (w,h) = (%.3f, %.3f)\n" % (self.width, self.height)
        ms_info += "\tresolution (pixels per unit) = %d\n" % self.ppu
        ms_info += "\tpixel size: (w,h) = (%d, %d)\n" % (self.px_width, self.px_height)
        ms_info += "\tmax. iterations = %d\n\n" % self.iters
        return ms_info

    def gen_mscreen(self):
        d = 1.0/self.ppu
        rows = []
        for iy in range(self.px_height):
            rows.append([])
            for ix in range(self.px_width):
                x = self.limits['low'].real + d*(0.5 + ix)
                y = self.limits['high'].imag - d*(0.5 + iy)
                rows[iy].append(MPoint(x,y))
        self.screen = rows

    def gen_mset(self):
        for row in self.screen:
            for pt in row:
                pt.Run_MFun(self.iters, complex(0,0))

    def get_img(self):
        img = []
        for iy in range(len(self.screen)):
            img.append([])
            for pt in self.screen[iy]:
                img[iy].append( self.cmap(pt.iter, self.iters) )
        return img
