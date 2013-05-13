import os
from os import path
from shutil import copy2, copytree, rmtree, ignore_patterns, Error

from mbrat.util import execSubproc, mb_mkdirs
    
from mbrat.configmgr import ConfigManager
from mbrat.settings import MBRAT_PROG, MBRAT_VER, MBRAT_PYD, MBRAT_PYVER, MBRAT_CONFD, \
    MBRAT_LIB_SRCD, MBRAT_LIB_OBJN_L, MBRAT_LIB_OBJEXT, MBRAT_HOME_USRD, MBRAT_CFG_TYPE_L, \
    MBRAT_ETCD, MBRAT_CMDF


def _install_libs(install_path):
    """ Pre-install required extension module shared object files into source directories. """

    build_path = path.join(install_path, 'build')
    print "Building MandelBrat library objects ...\n  -> {}".format(build_path)

    # execute 'python setup.py build_ext' in subprocess
    if not path.isdir(MBRAT_LIB_SRCD):
        return False
        
    libd = path.join(build_path, 'lib')
    run = execSubproc( [[MBRAT_PYVER, 'setup.py', 'build_ext', '--build-lib', libd],], 
                       shell=False )
    if not run:
        return False

    # copy shared library object into corresponding python package
    for objn in MBRAT_LIB_OBJN_L:
        objf = "_{0}.{1}".format(objn, MBRAT_LIB_OBJEXT)
        srcf = path.join(libd, objf)
        dstf = path.join( MBRAT_PYD, 'lib', objn, objf )

        print "==> Copying shared object {}".format(srcf)
        print "  -> {}".format(dstf)
        copy2(srcf, dstf)
        if not path.isfile( dstf ):
            print "==> ERROR: unable to copy {}".format(objf)
            return False

    # made it here? then we're good...
    return True


def _install_dirs(install_path):
    """ Pre-install required directory structure in user's $MBRAT_HOME directory. """

    print "Installing directory structure and files ..."

    if not mb_mkdirs(MBRAT_CONFD):
        print "==> ERROR: Unable to create {}".format(MBRAT_CONFD)
        return False

    # copy python scripts ...
    err_l = []
    try:
        copytree( path.join(install_path, 'mbrat'), path.join(MBRAT_CONFD, 'mbrat'), 
                  ignore=ignore_patterns('*.pyc', '*.pyx', '*~', '*#*'), symlinks=True )
    except Error as e:
        err_l.extend(e)

    # copy etc ...
    try:
        copytree( path.join(install_path, 'etc'), path.join(MBRAT_CONFD, 'etc'),
                  ignore=ignore_patterns('*~', '*#*'), symlinks=True )
    except Error as e:
        err_l.extend(e)

    # copy executable script ...
    copy2( path.join(install_path, 'mbrat.py'), path.join(MBRAT_CONFD) )
    if not path.exists( path.join(MBRAT_CONFD, 'mbrat.py') ):
        err_l.append( (path.join(install_path, 'mbrat.py'),
                       path.join(MBRAT_CONFD, 'mbrat.py'),
                       "unable to copy 'mbrat.py'") )

    # check for copy errors & exit if yep
    if err_l:
        for e in err_l:
            print str(e) + "\n"
        return False

    return True


def _install_usrd():
    
    print "Installing 'usr' configuration tree to\n  -> {}".format(MBRAT_HOME_USRD)

    if path.exists(MBRAT_HOME_USRD):
        print "==> ERROR: 'usr' dir already exists at\n  -> {}".format(MBRAT_HOME_USRD)
        return False

    # ... and use ConfigManager to do the rest
    cm = ConfigManager(usr_cfgf=path.join(MBRAT_HOME_USRD, 'usr.cfg'))
    print cm.logstr()
    e = cm.errstr()
    if e:
        print "==> ERROR: Unable to install because ...\n" + e
        return False

    return True


def _uninstall_usrd():

        print "Removing 'usr' tree from\n  -> {}".format(MBRAT_HOME_USRD)

        if not path.exists(MBRAT_HOME_USRD):
            print "==> ERROR: 'usr' config tree not found."
            return False

        rmtree(MBRAT_HOME_USRD)
        if path.exists(MBRAT_HOME_USRD):
            print "==> ERROR: Unable to remove 'usr' config tree."
            return False

        return True


def _install_exec():

    print "Installing '{0}' command at\n  -> {1}".format(MBRAT_PROG, MBRAT_CMDF)

    if path.isfile(MBRAT_CMDF):
        print "==> ERROR: Executable already exists."
        return False

    pyf = path.join(MBRAT_CONFD, "{}.py".format(MBRAT_PROG))
    tmp_cmd = path.join(MBRAT_ETCD, MBRAT_PROG)
    cmd_str = "#!/usr/bin/env bash\n" + \
              "exec \"{}\" \"$@\"\n".format(pyf)

    try:
        cmd_f = open(tmp_cmd, 'wb')
    except IOError as e:
        print "==> ERROR: {}".format(e.strerror)
        return False
    else:
        cmd_f.write(cmd_str)
        cmd_f.close()
        os.chmod(tmp_cmd, 0755)

    # copy temp command file into /usr/local/bin or elsewhere on $PATH
    run = execSubproc( [['sudo', 'cp', tmp_cmd, MBRAT_CMDF],], 
                       shell=False )
    if not run:
        return False

    if not path.isfile(MBRAT_CMDF):
        print "==> ERROR: Unable to create command executable script."
        return False

    return True


def _install_all(install_path):
    """ Install everything. """

    print "Installing everything ..."

    if path.exists(MBRAT_CONFD):
        print "==> ERROR: MandelBrat appears to be already installed."
        return False

    _install_usrd()

    if not _install_libs(install_path):
        return False
    if not _install_dirs(install_path):
        return False
    if not _install_exec():
        return False

    return True


def _uninstall():
    """ Uninstall everything. """

    print "Uninstalling resources (your 'usr' directory will remain untouched) ..."

    if not path.exists(MBRAT_CONFD):
        print "==> ERROR: MandelBrat is not installed."
        return False

    rmtree(MBRAT_CONFD, ignore_errors=True)
    if path.exists(MBRAT_CONFD):
        return False

    if path.isfile(MBRAT_CMDF):
        run = execSubproc( [['sudo', 'rm', MBRAT_CMDF],], 
                           shell=False )
        if not run:
            return False

    return True


def _breakdown():
    if _uninstall():
        return _uninstall_usrd()


def installMBrat(install_path, args):
    """ Switch installers. """

    print "MandelBrat ({0}-{1}) resource installer script.\n".format(MBRAT_PROG, MBRAT_VER)

    if args.uninstall:
        return _uninstall()
    elif args.reinstall:
        if not _uninstall():
            return False
        return _install_all(install_path)
    elif args.libs:
        return _install_libs(install_path)
    elif args.usr:
        return _install_usrd()
    elif args.rmusr:
        return _uninstall_usrd()
    elif args.breakdown:
        return _breakdown()
    else:
        return _install_all(install_path)
