from os import path
from mbrat.mscreen import PyMScreen

class Arguments(object):
    """
    An argument class with dict-parametric constructor. """

    def __init__(self, arg_d={}):
        for key, val in arg_d.iteritems():
            setattr(self, key, val)


def arglist_parse_to_dict(arg_l):
    """
    Function to parse either string or 2-D array arg lists into a dict. """

    prop_d = {}
    for prop in arg_l:
        if len(prop) == 2:
            prop_l = prop
        elif ':' in prop:
            prop_l = prop.split(':')
        elif '=' in prop:
            prop_l = prop.split('=')
        else:
            exit( "==> ERROR: invalid config. Use '=' or ':'." )
        if not len(prop_l) == 2:
            exit( "==> ERROR: invalid config. Use one '=' per setting." )
        prop_d[prop_l[0]] = prop_l[1]
    return prop_d


# mandelbrot set generic functions (too useful to be methods)

def pyMFun(c, z0, e, n):
    z = z0
    while n > 0:
        z = z*e*(c*c)
        n -= 1
    return z


def clogger(logstr, log_to_stdout=False):
    if log_to_stdout:
        print logstr
        logstr = ""
    return "{}\n".format(logstr)


def mpoint_pick_random(self, key_t, lts=False):
    """
    A function to pick a random point from a pool (MScreen). Takes a complete 
    ConfigManager instance as 'self'. Parameter 'key_t' is really just 'poolkey' 
    or 'privkey', but the function treats only 'poolkey' special. (Other key types
    besides 'privkey' are imaginable.)
    
    Returns an Argument object containing an MPoint instance, log, and error string.
    
    """
 
    errstr = ""
    logstr = clogger( "\nPicking a random {} key-point ...".format(key_t), lts )

    # current public pool config needed no matter what...
    pool_cfg = self.secmgr['pool']

    # public poolkey pool or not? (ie, privkey pool)
    if 'pool' in key_t:
        pool_t = 'pool'
        additers = 0
        keypool_cfg = pool_cfg
    else:
        pool_t = key_t
        additers = pool_cfg.get('iters')
        keypool_cfg = self.secmgr[key_t]
        keypool_cfg.set_section_to('pool')
        keypool_cfg.read()

    args = keypool_cfg.get_as_args()
    args.iters = int(args.iters) + int(additers)

    ms = PyMScreen(args)

    logstr += clogger( ms.get_info(), lts )

    imgf = keypool_cfg.get('image')
    if not imgf or not path.exists(imgf):
        # generate pool image file from MScreen and attach to config file ...
        imgf = path.join( keypool_cfg.rootd, "{}.png".format(keypool_cfg.get('name')) )
        logstr += clogger( "==> {} image not found. Making new one at\n".format(key_t) 
                           + "  -> {} ...".format(imgf),
                           lts )
        ms.gen_to_file(imgf)
        keypool_cfg.set_write( {'image': imgf,} )

    else:
        # ... else read PyMScreen object from image file
        logstr += clogger( "Reading image file ...", lts )
        try:
            ms.gen_mscreen_from_img(imgf)
        except Exception, err:
            errstr = clogger( "\n==> ERROR: {}".format(str(err)), lts )

    # MScreen method returns a random MPoint object
    pt = ms.get_mpoint()
    logstr += clogger( "\n==> Point picked: ({0}, {1})\n".format( pt.real, pt.imag )
                       + "  -> Index: [{0}, {1}]".format( pt.Get_ix(), pt.Get_iy() ),
                       lts )

    # update current *key config file
    self.secmgr[key_t].reset_section()
    self.secmgr[key_t].set_write( {'real': pt.real, 'imag': pt.imag,
                                   'info': "Randomly selected key-point.",} )

    return Arguments( {'log': logstr, 'err': errstr, 'mpoint': pt} )
