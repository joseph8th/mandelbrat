import os
from os import path

"""
MBrat core settings

"""

MBRAT_PROG = 'mbrat'
MBRAT_VER = '0.1g'

MBRAT_ROOT = os.getcwd()

MBRAT_LIB_SRCD = path.join(MBRAT_ROOT, 'src')
MBRAT_LIB_OBJN_L = ['mpoint',]
MBRAT_LIB_OBJEXT = 'so'

MBRAT_PYD = path.join(MBRAT_ROOT, 'mbrat')

MBRAT_USRD = path.join(MBRAT_ROOT, 'usr')
MBRAT_POOLSD = path.join(MBRAT_USRD, 'pools')
MBRAT_PROFILESD = path.join(MBRAT_USRD, 'profiles')
MBRAT_CURRENTL = '_current'

MBRAT_CFG_TYPE_L = ['pool', 'poolkey', 'profile', 'privkey', 'pubkey',]
MBRAT_EXTCFG_TYPE_L = MBRAT_CFG_TYPE_L[:].append('tmp')

MBRAT_CFG_DEPTREE_D = {
    'pool':    ['poolkey',],
    'poolkey': [],
    'profile': ['privkey', 'pubkey',],
    'privkey': [],
    'pubkey':  [],
    }

MBRAT_USR_CFGF = path.join(MBRAT_USRD, 'usr.cfg')

MBRAT_TMPD = path.join(MBRAT_USRD, 'tmp')
MBRAT_TMPF = path.join(MBRAT_TMPD, 'tmp.cfg')
MBRAT_TMP_IMGF = path.join(MBRAT_TMPD, 'tmp.png')

# some default settings...

MBRAT_DEF_PRECISION = 53
MBRAT_DEF_MPBACKEND = 'mpmath'

MBRAT_DEF_DRAW_D = { 
    'iters': 100, 'ppu': 96, 'cmap': "bw", 
    'lims': {'low':complex(-2.25, -1.25), 
             'high':complex(1.0, 1.25)},
    }

MBRAT_DEF_POOL_D = { 
    'pool': {
        'image': "",
        'cmap': "bw",
        'y_hi': "1.25", 'x_hi': "1.0",
        'y_lo': "-1.25", 'x_lo': "-2.25",
        'ppu': "96", 
        'iters': "100",
        'info': "New Point Pool. Use 'pool --set' to alter properties.",
        },
    }

MBRAT_DEF_POOLKEY_D = {
    'poolkey': {
        'info': "New Public Pool-Key. Use 'poolkey --set' to alter properties.",
        'pool': "skelpool",
        'real': "0.0",
        'imag': "0.0",
        'ix': "",
        'iy': "",
        },
    }

MBRAT_DEF_PRIVKEY_D = {
    'privkey': {
        'info': "New Private Key. Use 'privkey --set' to alter properties.",
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
