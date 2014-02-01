from distutils.core import setup, Extension
#from setuptools import setup, find_packages, Extension

from os import path
from mbrat.settings import MBRAT_PROG, MBRAT_VER


# C/++ extension modules
mpointc_module = Extension(
    '_mpoint',
#    include_dirs = ['/usr/include/python2.7'],
    libraries = ['gmp', 'mpfr',],
    sources = ['src/mpointc.c',],
)


# y'know... setup()
setup(
    name = MBRAT_PROG,
    version = MBRAT_VER,
    description = 'MandelBrat fractal crypto explorer.',
#    long_description = long_description,
    author = 'Joseph E Edwards VIII',
    author_email = 'joseph8th@notroot.us',
    url = 'https://github.com/joseph8th/mandelbrat',

#    packages = find_packages(),
#    scripts = ['install'],
#    install_requires = REQUIREMENTS,
    ext_modules = [mpointc_module],

    packages = ['mbrat', 'mbrat.commands', 'mbrat.spi', 
                'mbrat.mbrat_gui', 'mbrat.lib', 'mbrat.lib.mpoint',],
)
