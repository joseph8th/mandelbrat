import argparse
from mbrat.settings import MBRAT_PROG, MBRAT_VER

# instantiate arg parser
parser = argparse.ArgumentParser(prog=MBRAT_PROG, 
                                 description="tools for playing with mandelbrot crypto")
parser.add_argument("--version", action="version", version=MBRAT_VER)
subparsers = parser.add_subparsers(
    title="commands", 
    description="for command help, use '{} COMMAND -h'".format("mbrat"))
