
class Arguments(object):
    """
    An argument class with dict-parametric constructor. 
    Set the '__str__' and '__repr__' methods with method set_string(s).
    """

    def __init__(self, arg_d={}, string=None):

        for key, val in arg_d.iteritems():
            setattr(self, key, val)

#        self.set_string(string)

    def set_string(self, s):
        if not s:
            self.string = self
        else:
            self.string = s

 #   def __str__(self):
 #       return self.string

#    def __repr__(self):
#        return self.string


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



# general generic functions (too general to be methods)

def clogger(logstr, lts=False, err=False):
    """ 
    Function to route log to stdout, GUI console. """

    from sys import stdin, stderr

    # lts = log_to_stdout
    if lts:
        if not err:
            print "{}".format(logstr)
        else:
            stderr.write(logstr)
        logstr = ""

    return logstr


def mb_mkdirs(target):
    """
    Function to make directories or error back. """

    from os import makedirs, error
    try:
        makedirs(target, 0755)
    except error as e:
        print "==> ERROR: ({0}): {1}".format(e.errno, e.strerror)
        return False
    else:
        return True



def execSubproc(exelist, envdict=None, shell=True):
    """ 
    Function to execute commands in various ways. """

    from os import environ, path
    import subprocess

    # change environ of subprocess if nec.
    env = environ.copy()
    if envdict:
        for var, val in envdict.iteritems():
            env[var] = val

    # execute each command in the given list
    for exe in exelist:
        if shell:
            exe = " ".join(exe)
#        print "==> Executing command '{}' ...".format(exe)
        subproc = subprocess.Popen(exe, env=env, shell=shell,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        pout, perr = subproc.communicate()
        if pout:
            print pout
        if perr:
            print perr
            return False
 #       print "==> Execution complete."

    # all done executing commands? ok...
    return True


def mpoint_pick_random(self, key_t, lts=False):
    """
    A function to pick a random point from a pool (MScreen). Takes a complete 
    ConfigManager instance as 'self'. Parameter 'key_t' is really just 'poolkey' 
    or 'privkey', but the function treats only 'poolkey' special. (Other key types
    besides 'privkey' are imaginable.)
    
    Returns an Argument object containing an MPoint instance, log, and error string.
    
    """
 
    from os import path
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
    logstr += clogger( "\n==> Point picked: ({0}, {1})\n".format( pt.C.real, pt.C.imag )
                       + "  -> Index: [{0}, {1}]".format( pt.Get_ix(), pt.Get_iy() ),
                       lts )

    # update current *key config file
    self.secmgr[key_t].reset_section()
    self.secmgr[key_t].set_write( {'real': pt.C.real, 'imag': pt.C.imag,
                                   'ix': pt.Get_ix(), 'iy': pt.Get_iy(),
                                   'info': "Randomly selected key-point.",} )
    self.secmgr[key_t].read()

    return Arguments( {'log': logstr, 'err': errstr, 'mpoint': pt} )

