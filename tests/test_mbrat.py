#!/usr/bin/env python2

import warnings
from mpmath import mp, mpc
from mpmath import mpmathify as mpify

from mbrat.settings import MBRAT_CFG_DEPTREE_D, MBRAT_DEF_POOL_D, MBRAT_DEF_POOLKEY_D, \
    MBRAT_DEF_PRIVKEY_D
from mbrat.configmgr import ConfigManager
from mbrat.lib.mpoint import MPoint


secmgr_def_test_l = [MBRAT_DEF_POOL_D, MBRAT_DEF_POOLKEY_D, MBRAT_DEF_PRIVKEY_D,]

def test_cfgmgr_integrity(testno):
    print "\n[TEST %d]: ConfigManager-SecManager integrity check ..." % testno
    print "           (For different profile, check it out with '--ck' first.)" 

    cm = ConfigManager()

    for cfg_t in MBRAT_CFG_DEPTREE_D.keys():
        print "==> Checking current '%s' config profile ..." % cfg_t
        sm = cm.secmgr[cfg_t]
        sm_secs = sm.sections()
        print sm_secs
            

def test_mpoint_init(testno):
    test_prec = 15
    print "\n[TEST %d]: MPoint init at %d precision by ..." % (testno, test_prec)

    # setup test dict for 'complex' parameter types
    mpoint_test_d = {
        "complex_mpstr": [ '1.2323429893483498+23.452347567843234655676j', 
                         '1.2323429893483498-23.452347567843234655676j', 
                         '-1.2323429893483498+23.452347567843234655676j', 
                         '-1.2323429893483498-23.452347567843234655676j', ], 
        }
    mpoint_test_d.update( {
            "complex_py": [ complex(p) for p in mpoint_test_d["complex_mpstr"] ] 
            } )

    # ... for coordinate (x,y) paramater types, a shortcut for str coords
    mpoint_test_d.update( { 
            "coord_str": [ (str(p.real), str(p.imag)) 
                             for p in mpoint_test_d["complex_py"] ]
            } )
    mpoint_test_d.update( {
            "coord_ld": [ (p.real, p.imag) for p in mpoint_test_d["complex_py"] ]
            } )

    for test, param_l in mpoint_test_d.iteritems():
        print "==> " + test + ":"
        for param in param_l:
            if 'coord' in test:
                mpt = MPoint(param[0], param[1], test_prec)
            else:
                mpt = MPoint(param, test_prec)
            print "  -> %s\n  =? (%s, %s)" % (param, mpify(mpt.real), mpify(mpt.imag))

    # while we have an MPoint might as well test some other stuff...
    print "==> Testing MPoint.set_mp() and .C() multiprec return methods ..." 
    print "  -> none: ", mpt.C()
    mpt.set_mp('mpmath')
    print "  -> mpmath: ", mpt.C()
    mpt.set_mp('bigfloat')
    print "  -> bigfloat: ", mpt.C()


##### Here is the main function with pre-defs... #####

mbrat_test_l = [test_cfgmgr_integrity, test_mpoint_init, ]

if __name__ == '__main__':

    # Boost.Python BUG: we have to suppress RuntimeWarning on some linux
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        for ix in range(len(mbrat_test_l)):
            mbrat_test_l[ix](ix)
#        test_mpoint_init()
