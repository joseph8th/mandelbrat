from os import path

from mbrat.commander import Command
from mbrat.spi import Crypto

class CryptoCommand(Command):
    name = "crypto"
    description = "Cryptographic routines."
    help = "encryption and decryption routines"

    def __init__(self):
        super(CryptoCommand, self).__init__()
        self.group = self.parser.add_mutually_exclusive_group()
        self.group.add_argument( "--encrypt", "-e", action='store_true',
                                  help="encrypt the INFILE" )
        self.group.add_argument( "--decrypt", "-d", action='store_true',
                                  help="decrypt the INFILE" )
        self.parser.add_argument( "infile",
                                  help="the source file to encrypt or decrypt" )
        self.parser.add_argument( "outfile",
                                  help="the target output file" )
        self.parser.add_argument( "seckey",
                                  help="the secret key file (yeah I know thanks)" )

        self.parser.set_defaults(command=self)

        # instantiate a Crypto SPI object
        self.spi = Crypto()


    def run_command(self, args):
        if args.encrypt:
            self.run_encrypt(args)
        elif args.decrypt:
            self.run_decrypt(args)


    def run_encrypt(self, args):
        print "Encrypting '{0}' ...\n  -> '{1}'".format(args.infile, args.outfile)
        if not path.exists(args.infile):
            exit( "==> ERROR: infile not found:\n  -> {}".format(args.infile) )
        if not path.exists(args.seckey):
            exit( "==> ERROR: seckey not found:\n  -> {}".format(args.seckey) )

        inf = open(args.infile, 'r')
        plaintext = inf.read()
        inf.close()

        skf = open(args.seckey, 'r')
        seckey = skf.read()
        skf.close()

        ciphertext = self.spi.encrypt(plaintext, seckey)

        if ciphertext:
            outf = open(args.outfile, 'w')
            outf.write(ciphertext)
            outf.close()

        


    def run_decrypt(self, args):
        pass



# instantiate command
CryptoCommand()
