from _mpoint import *

from math import ceil
from mpmath import mp, mpmathify
from bigfloat import BigFloat, precision


MPoint.mp_t = None

# wrap mpoint string data in various multiprec objects...
def set_mp_t(self, mp_t):
    self.mp_t = mp_t

def get_mp_t(self):
    return self.mp_t

MPoint.set_mp = set_mp_t
MPoint.get_mp = get_mp_t


def C(self):
    if self.mp_t == 'mpmath':
        mp.dps = self.prec
        mpt = ( mpmathify(self.real), mpmathify(self.imag) )
    elif self.mp_t == 'bigfloat':
        mpt = ( BigFloat.exact(self.real, precision=int(ceil(self.prec*3.33))), 
                BigFloat.exact(self.imag, precision=int(ceil(self.prec*3.33))) )
    else:
        mpt = self.c

    return mpt


def Real(self):
    if self.mp_t == 'mpmath':
        mp.dps = self.Get_Prec()
        x = mpmathify(self.real)
    elif self.mp_t == 'bigfloat':
        x = BigFloat.exact(self.real, precision=int(ceil(self.prec*3.33)))
    else:
        x = self.real

    return x


def Imag(self):
    if self.mp_t == 'mpmath':
        mp.dps = self.Get_Prec()
        y = mpmathify(self.imag)
    elif self.mp_t == 'bigfloat':
        y = BigFloat.exact(self.imag, precision=int(ceil(self.prec*3.33)))
    else:
        y = self.imag

    return y


# now let these methods be members of MPoint...
MPoint.BigC = C
MPoint.Real = Real
MPoint.Imag = Imag
