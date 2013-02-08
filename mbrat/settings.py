import os
from os import path

MBRAT_ROOT = os.getcwd()

MBRAT_LIBD = path.join(MBRAT_ROOT, 'lib')
MBRAT_LIBMPOINTF = path.join(MBRAT_LIBD, 'mpoint.so')

MBRAT_PYD = path.join(MBRAT_ROOT, 'mbrat')

"""
MBrat GUI settings
"""
MBRAT_GUID = path.join(MBRAT_PYD, 'mbrat_gui')
MBRAT_GUID_GLADEF = path.join(MBRAT_GUID, 'mbrat_gui.glade') 

MBRAT_TMPD = path.join(MBRAT_ROOT, 'tmp')
MBRAT_TMP_IMGF = path.join(MBRAT_TMPD, 'tmp.png')

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
