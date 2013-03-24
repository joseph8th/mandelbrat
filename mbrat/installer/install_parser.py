import argparse
from mbrat.settings import MBRAT_PROG, MBRAT_VER
from install import installMBrat

def installparser():
    description = "Installation utils for {} v{}.".format(MBRAT_PROG, MBRAT_VER)
    parser_install = argparse.ArgumentParser(description=description)
    install_group = parser_install.add_mutually_exclusive_group()
    install_group.add_argument("-l", "--libs", action="store_true",
                               help="make and install shared object library files")
#    install_group.add_argument("-i", "--install", action="store_true",
#                               help="DEFAULT: install {}".format(PYVENV_PROG_VER))
#    install_group.add_argument("-r", "--reinstall", action="store_true",
#                               help="uninstall/install {}".format(PYVENV_PROG_VER))
#    install_group.add_argument("-u", "--uninstall", action="store_true",
#                               help="uninstall {}".format(PYVENV_PROG_VER))
    parser_install.set_defaults(func=installMBrat)

    return parser_install.parse_args()
