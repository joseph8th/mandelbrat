class MBratSPI(object):

    def __init__(self, svcfun=None, hashsvc=None):
        self.set_function(svcfun)
        self.set_hashsvc(hashsvc)

    def set_function(self, svcfun):

        if not svcfun:
            from mbrat.functions import MandelFun
            svcfun = MandelFun

        self.function = svcfun

    def set_hashsvc(self, hashsvc):

        if not hashsvc:
            from hashlib import md5
            hashsvc = md5

        self.hasher = hashsvc

    def run(self, args):
        return self.run_service(args)


class SignSPI(MBratSPI):

    def __init__(self, svcfun):
        super(SignSPI, self).__init__(svcfun)

    def run_service(self, args):

        # first hash the plaintext with MD5
        hashtext = self.hasher(args.plaintext).hexdigest()

        # feed it to MFun
        sighash = []
        for i in range(len(hashtext)):
            sighash.append(hashtext[i])

        return sighash



class ValidateSPI(object):

    def __init__(self, svcfun):
        super(ValidateSPI, self).__init__(svcfun)

    def run_service(self, args):

        # hash the plaintext like the source did

        hashtext = self.hasher(args.plaintext).hexdigest()

        # also feed it to MFun for comparison ...

        hashary = array('c', hashtext)

        for i in len(hashtext):
            print hashary[i]

        return args.plaintext
