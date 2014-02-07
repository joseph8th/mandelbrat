from os import path

from mbrat.util import Arguments, clogger
from mbrat.settings import MBRAT_DEF_MPBACKEND, MBRAT_DEF_PRECISION



def mlmul(u, v):
    """ Multi-library multiplication function. """

    if u.mp_t != v.mp_t:
        return None

    if u.mp_t == 'bigfloat':

        from bigfloat import BigFloat, mul

        z_real = mul(u.mp_c.real, v.mp_c.real) - \
                 mul(u.mp_c.imag, v.mp_c.imag)

        z_imag = mul(u.mp_c.real, v.mp_c.imag) + \
                 mul(u.mp_c.imag, v.mp_c.real)

        z = Arguments({'real': z_real, 'imag': z_imag})

    else:

        from mpmath import fmul

        z = fmul(u.mp_c, v.mp_c)
    
    return MultiLibMPC(z.real, z.imag, u.mp_t, u.prec)



class MandelFun(object):
    """ 
    Provides methods used to compute multi-privkey key types.
    Takes MultiLibMPC objects as parameters. 
    """

    def run(self, c, z0, e, n):
        
        z = z0
        while n > 0:
            z = mlmul(z, mlmul(e, mlmul(c, c)))
            n -= 1

        return z



class MultiLibMPC(object):
    """
    A 'complex' multi-precision object using choice of MP library. """

    def __init__(self, raw_x, raw_y, 
                 mp_t=MBRAT_DEF_MPBACKEND, 
                 prec=MBRAT_DEF_PRECISION):

        self.mp_t = mp_t
        self.raw_c = (raw_x, raw_y)
        
        if self.mp_t == 'bigfloat':
            self.prec = int(ceil(prec * MBRAT_PREC_FACTOR))
            self.mp_c = self.mk_bfc(raw_x, raw_y)
        else:
            self.prec = int(prec)
            self.mp_c = self.mk_mpc(raw_x, raw_y)


    def mk_mpc(self, x, y):

        from mpmath import mp, mpc
        from mpmath import mpmathify as mpify

        mp.dps = int(self.prec)

        return mpc( real = mpify(x), imag = mpify(y) )


    def mk_bfc(self, x, y):

        from bigfloat import BigFloat, precision
        from mbrat.util import Arguments

        with precision(self.prec):
            bf_x = BigFloat.exact(x)
            bf_y = BigFloat.exact(y)

        return Arguments(
            {'real': bf_x, 'imag': bf_y},
            string="bfc(real='{0}', imag='{1}')".format(bf_x, bf_y) )


    def real(self):
        return self.mp_c.real


    def imag(self):
        return self.mp_c.imag


    def __repr__(self):

        if self.mp_t == 'bigfloat':
            rep = ( 'MultiLibMPC(real=%s imag=%s)'
                    % (repr(self.mp_c.real), repr(self.mp_c.imag)) )
        else:
            rep = ( 'MultiLibMPC(real=%s imag=%s precision=%s)' 
                    % (repr(self.mp_c.real), repr(self.mp_c.imag), 
                       repr(self.prec)) )

        return rep
        


def mpoint_pick_random(self, key_t, lts=False):
    """
    A function to pick a random point from a pool (MScreen). Takes a 
    ConfigManager instance as 'self'. Parameter 'key_t' is just 'poolkey' 
    or 'privkey', but the function treats 'poolkey' special. (Other key types
    besides 'privkey' are imaginable.)
    
    Returns an Arguments object containing an MPoint, and log/error strings.
    
    """

    from mbrat.lib.mscreen import PyMScreen
 
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
        imgf = path.join( 
            keypool_cfg.rootd, "{}.png".format(keypool_cfg.get('name')) )
        logstr += clogger( 
            "==> {} image not found. Making new one at\n".format(key_t) 
            + "  -> {} ...".format(imgf),
            lts )
        ms.gen_to_file(imgf)
        keypool_cfg.set_write( {'image': imgf,} )

    else:
        # ... else read PyMScreen object from image file
        logstr += clogger( "Reading image file ...", lts )
        try:
            ms.gen_mscreen_from_img(imgf)
        except Exception as err:
            errstr = clogger( "\n==> ERROR: {}".format(str(err)), lts )

    # MScreen method returns a random MPoint object
    pt = ms.get_mpoint()
    logstr += clogger( 
        "\n==> Point picked: ({0}, {1})\n".format( pt.C.real, pt.C.imag )
        + "  -> Index: [{0}, {1}]".format( pt.Get_ix(), pt.Get_iy() ),
        lts )

    # update current *key config file
    self.secmgr[key_t].reset_section()
    self.secmgr[key_t].set_write( {'real': pt.C.real, 'imag': pt.C.imag,
                                   'ix': pt.Get_ix(), 'iy': pt.Get_iy(),
                                   'info': "Randomly selected key-point.",} )
    self.secmgr[key_t].read()

    return Arguments( {'log': logstr, 'err': errstr, 'mpoint': pt} )
