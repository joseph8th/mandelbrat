import os
from os import path
import argparse
import png

from mbrat.commander import Command
from mbrat.mscreen import PyMScreen
from mbrat.configmgr import ConfigManager
from mbrat.settings import MBRAT_POOLSD, MBRAT_DEF_DRAW_D, cmap_bw, cmap_gs


class LimitsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        x_lo = min([values[0], values[2]])
        x_hi = max([values[0], values[2]])
        y_lo = min([values[1], values[3]])
        y_hi = max([values[1], values[3]])
        values = {
            'low': complex(x_lo, y_lo), 'high': complex(x_hi, y_hi), 
            }
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
        self.parser.add_argument("-r", dest="ppu", type=int, 
                                 default = MBRAT_DEF_DRAW_D['ppu'],
                                 help="image resolution in pixels per unit")
        self.parser.add_argument("-l", dest="lims", nargs=4, type=float,
                                 default = MBRAT_DEF_DRAW_D['lims'],
                                 action=LimitsAction,
                                 help="x_lo y_lo x_hi y_hi")
        self.parser.add_argument("-i", dest="iters", type=int, 
                                 default = MBRAT_DEF_DRAW_D['iters'],
                                 help="maximum iterations to attempt")
        self.parser.add_argument("-c", dest="cmap", 
                                 choices=['bw', 'grey'], 
                                 default = MBRAT_DEF_DRAW_D['cmap'],
                                 help="color map to use (default: bw)")
        self.parser.add_argument("-p", dest='profile', action='store_true',
                                 help="use pool given by FILENAME")
        self.parser.add_argument("-s", dest='save', action='store_true',
                                 help="save image in new pool config named FILENAME")
        self.parser.add_argument("filename", action=FilenameAction,
                                 help="image filename (OR pool name if '-p' given)")
        self.parser.set_defaults(command=self)

        self.cfgmgr = ConfigManager()
        self.config = self.cfgmgr.secmgr['pool']


    def run_command(self, args):
        poolname, fext = path.splitext(args.filename)
        args.prop_d = {'name': poolname,}

        if args.save:
            args = self._mkpool_from_args(args)
        if args.profile:
            args = self._parse_cfg_to_args(args)

        # instantiate a new MScreen and draw to file no matter what...
        ms = PyMScreen(args)
        ms.gen_to_file(args.filename)
        print "Generating Mandelbrot set to\n--> {} ...\n".format(args.filename)
        print ms.get_info()


    def _parse_lims_to_dict(self, args):
        pd = args.prop_d

        if 'lims' in pd:
            l = pd['lims']
            pd['x_lo'] = l['low'].real
            pd['y_lo'] = l['low'].imag
            pd['x_hi'] = l['high'].real
            pd['y_hi'] = l['high'].imag

        del args.prop_d['lims']
        return args


    def _mkpool_from_args(self, args):
        cm = self.cfgmgr
        sm = self.config
        pd = args.prop_d

        print "Making new pool '{}' ...".format(pd['name'])
        cm.make_config('pool', pd['name'])
        sm.set_configf_by_name(pd['name'])

        # update and reformat the prop_d for later set_write
        for key in MBRAT_DEF_DRAW_D.keys():
            pd[key] = getattr(args, key)

        args = self._parse_lims_to_dict(args)
        args.prop_d.update( {
                'info': "Made by 'draw -s' command. Use 'pool --set' to alter.",
                'image': "", 
                } )
        sm.set_write(args.prop_d)
        args.profile = True

        return args


    def _parse_cfg_to_args(self, args):
        cm = self.cfgmgr
        sm = self.config
        pd = args.prop_d

        poolf = cm.get_configf( 'pool', pd['name'] )
        if not poolf:
            exit( "==> ERROR: pool config '{}' not found".format(pd['name']) )

        sm.set_configf_by_name(pd['name'])
        cfg_args = sm.get_as_args()
        cfg_args.filename = path.join( sm.rootd, args.filename )
        sm.set_write( {'image': cfg_args.filename,} )

        return cfg_args


# instantiate command
DrawCommand()
