from gmpy2 import mpc


class SignatureSPI(object):

    def __init__(self, svcfun=None, hashsvc=None):
        self.set_function(svcfun)
        self.set_hashsvc(hashsvc)


    def set_function(self, svcfun):

        if not svcfun:
            from mbrat.mutil import mandelfun
            svcfun = mandelfun

        self.function = svcfun


    def set_hashsvc(self, hashsvc):

        if not hashsvc:
            from hashlib import md5
            hashsvc = md5

        self.hasher = hashsvc


    def run(self, args):
        return self.run_service(args)



class SignSPI(SignatureSPI):

    def __init__(self, svcfun):
        super(SignSPI, self).__init__(svcfun)


    def _hash2mpc(self, hashtext, prec):
        
        # first split the hashtext in two
        reals_txt = hashtext[:(len(hashtext)/2)]
        imags_txt = hashtext[(len(hashtext)/2):]

        mpc_l = []
        for i in range(len(hashtext)/2):
            mpc_l.append( mpc( 1.0 / float(ord(reals_txt[i])), 
                               1.0 / float(ord(imags_txt[i])), 
                               precision=prec ) )
        
        return mpc_l


    def run_service(self, args):

        # first hash the plaintext with MD5
        hash_txt = self.hasher(args.plaintext).hexdigest()

        # format it for MFun
        hash_mpc = self._hash2mpc(hash_txt, args.spi['prec'])

        # feed it to MFun
        hash_sig = []
        for i in range(len(hash_mpc)):
            
            hash_sig.append( self.function(args.spi['poolkey'], 
                                           hash_mpc[i],
                                           args.spi['privkey'],
                                           args.spi['iters']
                                           ) )

        return hash_sig



class ValidateSPI(SignatureSPI):

    def __init__(self, svcfun):
        super(ValidateSPI, self).__init__(svcfun)

    def run_service(self, args):

        # hash the plaintext like the source did, but with diff privkey

        sign_spi = SignSPI(self.function)
        hash_sig = sign_spi.run(args)

        # also feed it to MFun for comparison ...

###########333
        print hash_sig

#        hashary = array('c', hashtext)
#        for i in len(hashtext):
#            print hashary[i]

        return args.plaintext
