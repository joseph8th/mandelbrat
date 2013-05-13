import argparse
from mbrat.settings import MBRAT_PROG, MBRAT_VER
from install import installMBrat

def installparser():
    description = "Installation utils for {} v{}.".format(MBRAT_PROG, MBRAT_VER)
    parser_install = argparse.ArgumentParser(description=description)
    install_group = parser_install.add_mutually_exclusive_group()
    install_group.add_argument("--libs", action="store_true",
                               help="make and install shared object library files")
    install_group.add_argument("--usr", action="store_true",
                               help="create 'usr' tree in user's $HOME/.config")
    install_group.add_argument("--rmusr", action="store_true",
                               help="delete 'usr' tree")
    install_group.add_argument("--install", action="store_true",
                               help="DEFAULT: install {}".format(MBRAT_PROG))
    install_group.add_argument("--reinstall", action="store_true",
                               help="uninstall/install {}".format(MBRAT_PROG))
    install_group.add_argument("--uninstall", action="store_true",
                               help="uninstall {}".format(MBRAT_PROG))
    install_group.add_argument("--breakdown", action="store_true",
                               help="uninstall AND remove 'usr' tree")
    parser_install.set_defaults(func=installMBrat)

    return parser_install.parse_args()
