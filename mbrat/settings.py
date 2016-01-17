import os
from os import path

#from mbrat.define import MBRAT_PROG, MBRAT_VER, MBRAT_PYVER, \
    #DEF_COMMANDD, DEF_ROOTD, DEF_MAINF, DEF_USRD, DEF_CONFD

######################################################################
# MBrat core settings
######################################################################

MBRAT_PROG='mbrat'
MBRAT_VER='0.3'
MBRAT_PYVER='2.7'

MBRAT_ROOT = os.getcwd()
MBRAT_CONFD = MBRAT_ROOT   # in case we want to separate data later

# needed during installation to $HOME but will work for standalone clone too
MBRAT_LIB_SRCD = path.join(MBRAT_ROOT, 'src')
MBRAT_LIB_OBJN_L = ['mpoint',]
MBRAT_LIB_OBJEXT = 'so'

MBRAT_PYD = path.join(MBRAT_ROOT, 'mbrat')

MBRAT_ETCD = path.join(MBRAT_ROOT, 'etc')

# data paths
MBRAT_USRD = path.join(MBRAT_CONFD, 'usr')
MBRAT_USR_CFGF = path.join(MBRAT_USRD, 'usr.cfg')
MBRAT_POOLSD = path.join(MBRAT_USRD, 'pools')
MBRAT_PROFILESD = path.join(MBRAT_USRD, 'profiles')
MBRAT_CURRENTL = '_current'

MBRAT_TMPD = path.join(MBRAT_USRD, 'tmp')
MBRAT_TMPF = path.join(MBRAT_TMPD, 'tmp.cfg')
MBRAT_TMP_IMGF = path.join(MBRAT_TMPD, 'tmp.png')

MBRAT_CFG_TYPE_L = ['pool', 'poolkey', 'profile', 'privkey', 'pubkey',]
MBRAT_EXTCFG_TYPE_L = MBRAT_CFG_TYPE_L[:].append('tmp')

MBRAT_CFG_DEPTREE_D = {
    'pool':    ['poolkey',],
    'poolkey': [],
    'profile': ['privkey', 'pubkey',],
    'privkey': [],
    'pubkey':  [],
    }

# some default settings...

MBRAT_PREC_FACTOR = 3.3
MBRAT_DEF_PRECISION = 16
MBRAT_DEF_PREC_BITS = MBRAT_DEF_PRECISION * MBRAT_PREC_FACTOR
MBRAT_DEF_MPBACKEND = 'mpmath'

MBRAT_DEF_DRAW_D = {
    'iters': 100, 'ppu': 96, 'cmap': "bw",
    'lims': {'low':complex(-2.25, -1.25),
             'high':complex(1.0, 1.25)},
}

MBRAT_DEF_USR_D = {
    'prefs': {
        'savetemp': "True",
        'showpoints': "True",
        'lts': "False",
        'mpbackend': MBRAT_DEF_MPBACKEND,
    },
}

MBRAT_DEF_POOL_D = {
    'pool': {
        'image': "",
        'cmap': "bw",
        'y_hi': "1.25", 'x_hi': "1.0",
        'y_lo': "-1.25", 'x_lo': "-2.25",
        'ppu': "96",
        'iters': "100",
        'info': "Point Pool. Use 'pool --set' to alter properties.",
    },
}

MBRAT_DEF_POOLKEY_D = {
    'poolkey': {
        'info': "Public Pool-Key. Use 'poolkey --set' to alter properties.",
        'pool': "skelpool",
        'real': "-0.001",
        'imag': "0.001",
        'ix': "",
        'iy': "",
    },
}

MBRAT_DEF_PRIVKEY_D = {
    'privkey': {
        'info': "Private Key. Use 'privkey --set' to alter properties.",
        'prec': "53",
        'real': "0.001",
        'imag': "-0.001",
        'ix': "",
        'iy': "",
    },
    'pool': {
        'image': "",
        'cmap': "bw",
        'y_hi': "1.25", 'x_hi': "1.0",
        'y_lo': "-1.25", 'x_lo': "-2.25",
        'ppu': "96",
        'iters': "25",
    },
}


"""
Color map functions

"""

def cmap_fun(cmap):
    if 'grey' in cmap:
        return cmap_gs
    else:
        return cmap_bw

def cmap_bw(iters, itermax):
    return 255 if iters != itermax else 0

def cmap_gs(iters, itermax):
    return (255 - int(iters*255/itermax)) % 256


"""
MBrat GUI settings

"""

MBRAT_GUID = path.join(MBRAT_PYD, 'mbrat_gui')
MBRAT_GUID_GLADEF = path.join(MBRAT_GUID, 'mbrat_gui.glade')

"""
Some defaults and settings helper structs...

"""
MBRAT_GUI_POOL_TYPE_L = ['tmp', 'pool', 'privkey',]

# a dict to map out the parent/child relations among elts...
MBRAT_GUI_DEPTREE_D = {
    'param': {
        'tmp': [ "saveToPoolButton", ],
        },
    'profile': {
        'pool': [ "profilePoolKeyCombobox", "pickPoolKeyButton", ],
        'poolkey': [ "poolkeyPickerButton", ],
        'profile': [ "profilePrivKeyCombobox", "pickPrivKeyButton", ],
        'privkey': [ "privkeyPickerButton",
                     "profilePubKeyCombobox", "addPubKeyButton", ]
        },
    }
