from _mpoint import *

from math import ceil
from mpmath import mp, mpmathify
from bigfloat import BigFloat, precision

from mbrat.mutil import MultiLibMPC as mlmpc
from mbrat.settings import MBRAT_PREC_FACTOR

MPoint.mp_t = None

# wrap mpoint string data in various multiprec objects...
def set_mp_t(self, mp_t):
    self.mp_t = mp_t

def get_mp_t(self):
    return self.mp_t

MPoint.set_mp = set_mp_t
MPoint.get_mp = get_mp_t

def mp_c(self):
    return mlmpc(self.real, self.imag, self.mp_t, self.prec)

MPoint.mp_c = mp_c

#def C(self):
#    return self.mp_c()

    #if self.mp_t == 'mpmath':
    #    mp.dps = self.prec
    #    mpt = ( mpmathify(self.real), mpmathify(self.imag) )
    #elif self.mp_t == 'bigfloat':
    #    mpt = ( 
    #        BigFloat.exact(
    #            self.real, precision=int(ceil(self.prec*MBRAT_PREC_FACTOR))), 
    #        BigFloat.exact(
    #            self.imag, precision=int(ceil(self.prec*MBRAT_PREC_FACTOR))) 
    #    )
    #else:
    #    mpt = self.c
    #return mpt


def Real(self):
    return self.mp_c().real

    #if self.mp_t == 'mpmath':
    #    mp.dps = self.Get_Prec()
    #    x = mpmathify(self.real)
    #elif self.mp_t == 'bigfloat':
    #    x = BigFloat.exact(
    #        self.real, precision=int(ceil(self.prec*MBRAT_PREC_FACTOR)))
    #else:
    #    x = self.real
    #return x


def Imag(self):
    return self.mp_c().imag

    #if self.mp_t == 'mpmath':
    #    mp.dps = self.Get_Prec()
    #    y = mpmathify(self.imag)
    #elif self.mp_t == 'bigfloat':
    #    y = BigFloat.exact(
    #        self.imag, precision=int(ceil(self.prec*MBRAT_PREC_FACTOR)))
    #else:
    #    y = self.imag
    #return y


def __repr__(self):
    return ( 'MPoint(real=%s imag=%s precision=%s)'
             % ( repr((self.mp_c()).real), repr((self.mp_c()).imag), 
                 repr(ceil((self.mp_c()).prec)) ) )


# now let these methods be members of MPoint...
#MPoint.BigC = C
MPoint.Real = Real
MPoint.Imag = Imag
MPoint.__repr__ = __repr__
