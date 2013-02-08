import os
import argparse
import png
from mbrat.commander import Command
from mbrat.mscreen import PyMScreen
from mbrat.settings import cmap_bw, cmap_gs

class LimitsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        x_lo = min([values[0], values[2]])
        x_hi = max([values[0], values[2]])
        y_lo = min([values[1], values[3]])
        y_hi = max([values[1], values[3]])
        values = {'low':complex(x_lo, y_lo), 'high':complex(x_hi, y_hi)}
        setattr(namespace, self.dest, values)

class FilenameAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not '.png' in os.path.splitext(os.path.basename(values)):
            values = values + ".png"
        setattr(namespace, self.dest, values)

class DrawCommand(Command):
    name = "draw"
    description = "Draw a Mandelbrot set to PNG file."
    help = "draw Mandelbrot set to file"

    def __init__(self):
        super(DrawCommand, self).__init__()
        self.parser.add_argument("-r", dest="ppu", type=int, default=75,
                                 help="image resolution in pixels per unit (default: 75)")
        self.parser.add_argument("-l", dest="lims", nargs=4, type=float,
                                 default={'low':complex(-2.5, -1.0), 
                                          'high':complex(1.0, 1.0)}, 
                                 action=LimitsAction,
                                 help="X_lo Y_lo X_hi Y_hi")
        self.parser.add_argument("-i", dest="iters", type=int, default=100,
                                 help="maximum iterations to attempt (default: 100)")
        self.parser.add_argument("-c", dest="cmap", 
                                 choices=['bw', 'grey'], default="bw",
                                 help="color map to use (default: bw)")
        self.parser.add_argument("filename", action=FilenameAction,
                                 help="path to and name of target image")
        self.parser.set_defaults(command=self)

    def run_command(self, args):
        ms = PyMScreen(args)
        print ms.get_info()

        print "\nGenerating Mandelbrot set ..."
        ms.gen_mscreen()
        ms.gen_mset()

        print "Generating image ..."
        img = ms.get_img()

        print "Writing to %s ..." % os.path.abspath(args.filename)
        f = open(args.filename, 'wb')
        w = png.Writer(len(img[0]), len(img), greyscale=True, bitdepth=8)
        w.write(f, img)
        f.close()

# instantiate command
DrawCommand()
