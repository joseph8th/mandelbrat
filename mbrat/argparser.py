import argparse

# instantiate arg parser
parser = argparse.ArgumentParser(prog="mbrat", 
                                 description="tools for playing with mandelbrot crypto")
parser.add_argument("--version", action="version", version='0.0')
subparsers = parser.add_subparsers(
    title="commands", 
    description="for command help, use '{} COMMAND -h'".format("mbrat"))
