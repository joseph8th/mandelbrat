
# mandelbrot set generic functions (too useful to be methods)

def pyMFun(c, z0, e, n):
    """ 
    Function used to compute multi-privkey key types (pubkey, seckey). """

    from mpmath import mp, mpc, fmul

    z = mpc(z0)    

    while n > 0:
        z = fmul(z, fmul(e, fmul(c, c)))
        n -= 1

    return z
