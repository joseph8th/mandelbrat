from install_parser import installparser

def main(install_path):
    args = installparser()
    # check if system user space is config'd or not
    if not args.func(install_path, args):
        exit("Error: unable to complete operation.")
    else:
        print "Success! Operation completed."
        exit()
