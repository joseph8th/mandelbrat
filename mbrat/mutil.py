from os import path
from bigfloat import BigFloat, mul
#from mpmath import mp, mpc, fmul

from mbrat.util import Arguments
from mbrat.mscreen import PyMScreen


# mandelbrot set generic functions (too useful to be methods)

def pyMFun(c, z0, e, n):
    z = BigFloat.exact(z0)
    while n > 0:
        z = mul(z, mul(e, mul(c, c)))
        n -= 1
    return z


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
    self.secmgr[key_t].read()

    return Arguments( {'log': logstr, 'err': errstr, 'mpoint': pt} )
