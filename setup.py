import os
from distutils.core import setup, Extension
from mbrat.settings import MBRAT_PROG, MBRAT_VER

README = os.path.join(os.path.dirname(__file__), 'PKG-INFO')
long_description = open(README).read() + "\n"

mpoint_module = Extension(
    '_mpoint',
    include_dirs = ['/usr/include/python2.7'],
    libraries = ['boost_python', 'python2.7', 'mpfr', 'gmp'],
    sources = ['src/mpoint.cpp'],
)

setup(
    name = MBRAT_PROG,
    version = MBRAT_VER,
    description = 'MandelBrat fractal crypto explorer.',
    long_description = long_description,
    author = 'Joseph E Edwards VIII',
    author_email = 'joseph8th@notroot.us',
    url = 'https://github.com/joseph8th/mandelbrat',

    ext_modules = [mpoint_module],

    packages = ['mbrat', 'mbrat.commands', 'mbrat.spi', 
                'mbrat.mbrat_gui', 'mbrat.lib', 'mbrat.lib.mpoint',],
)
