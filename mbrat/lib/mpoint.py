from gmpy2 import mpc, mul, add, norm


class MPoint(object):

    iters = 0
    inmset = False
    index = None

    def __init__(self, C_in, prec_in):

        self.C = mpc(C_in)
        self.prec = prec_in

        
    def Run_MFun(itermax, Z_0):

        gmpy2.get_context().precision = self.prec

        Z = mpc(Z_0)

        while self.iters < itermax:
            Z = add( gmpy2.mul(Z,Z), self.C )
            if norm(Z) > 4.0:
                break
            self.iters += 1
            
        if self.iters == itermax:
            self.inmset = True
            
