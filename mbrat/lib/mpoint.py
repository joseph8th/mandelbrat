import gmpy2
from gmpy2 import mpc, mul, add, norm


class MPoint(object):

    iters = 0
    inmset = False
    index = (-1,-1)

    def __init__(self, C_in, prec_in):

        self.C = C_in
        self.prec = prec_in

        
    def Run_MFun(self, itermax, Z_0):
        """ Expects gmpy2.mpc type for Z_0. """

        if not gmpy2.get_context().precision == self.prec:
            gmpy2.get_context().precision = self.prec

        Z = Z_0

        while self.iters < itermax:
            Z = add( gmpy2.mul(Z,Z), self.C )
            if norm(Z) > 4.0:
                break
            self.iters += 1
            
        if self.iters == itermax:
            self.inmset = True
            

    def Set_Index(self, ix, iy):
        self.index = (ix, iy)


    def Get_ix(self):
        return self.index[0]

    def Get_iy(self):
        return self.index[1]

    def Get_Index(self):
        return self.index
