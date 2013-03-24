import os
from os import path
#from shutil import copy2, rmtree

from mbrat.settings import MBRAT_PYD, MBRAT_LIB_SRCD, MBRAT_LIB_OBJN_L, MBRAT_LIB_OBJEXT
from mbrat.util import execSubproc


def installMBrat(install_path, args):
    if args.libs:
        return installLibs(install_path, args)


def installLibs(install_path, args):
    print "Installing MandelBrat library objects into install path:"
    print "  -> " + install_path

    for objn in MBRAT_LIB_OBJN_L:
        objf = "{0}.{1}".format(objn, MBRAT_LIB_OBJEXT)
        print "==> Making shared object '{}' in source directory:".format(objf)
        print "  -> " + MBRAT_LIB_SRCD

        # execute 'make' in subprocess in 'src' dir...
        if not path.isdir(MBRAT_LIB_SRCD):
            return False
        
        os.chdir(MBRAT_LIB_SRCD)
        run = execSubproc( [['make', objn,],], shell=False )
        os.chdir(install_path)
        if not run:
            return False
    
        print "==> Copying shared object file to target module directory:"
        print "  -> " + MBRAT_PYD


    # made it here? then we're good...
    return True
