from os import path

from mbrat.commander import Command
from mbrat.configmgr import ConfigManager

class CryptCommand(Command):
    name = "crypt"
    description = "Encryption and decryption using current profile privkey."
    help = "encryption and decryption"

    def __init__(self):
        super(CryptCommand, self).__init__()
        self.group = self.parser.add_mutually_exclusive_group()
        self.group.add_argument( "--encrypt", "-e", action='store_true',
                                  help="encrypt the INFILE" )
        self.group.add_argument( "--decrypt", "-d", action='store_true',
                                  help="decrypt the INFILE" )
        self.parser.add_argument( "infile",
                                  help="the source file" )
        self.parser.add_argument( "outfile",
                                  help="the target output file" )

        self.parser.set_defaults(command=self)


    def run_command(self, args):
        if args.encrypt:
            self.run_encrypt(args)
        elif args.decrypt:
            self.run_decrypt(args)


    def run_encrypt(self, args):

        from mbrat.spi.encrypt import Encrypt

        spi = Encrypt()

        print "Encrypting '{0}' ...\n  -> '{1}'".format(args.infile, args.outfile)
        if not path.exists(args.infile):
            exit( "==> ERROR: infile not found:\n  -> {}".format(args.infile) )
        inf = open(args.infile, 'r')
        plaintext = inf.read()
        inf.close()

        ciphertext = spi.encrypt(plaintext)

        if ciphertext:
            outf = open(args.outfile, 'w')
            outf.write(ciphertext)
            outf.close()

        


    def run_decrypt(self, args):
        pass



# instantiate command
CryptCommand()
