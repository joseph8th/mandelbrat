from mbrat.settings import MBRAT_PROG, MBRAT_VER
from distutils.core import setup, Extension

mpoint_module = Extension(
    '_mpoint',
    include_dirs = ['/usr/include/python2.7'],
    libraries = ['boost_python', 'python2.7', 'mpfr', 'gmp'],
    sources = ['src/mpoint.cpp']
    )

setup (
    name = MBRAT_PROG,
    version = MBRAT_VER,
    description = 'MandelBrat the fractal crypto explorer.',
    author = 'Joseph E Edwards VIII',
    author_email = 'joseph8th@urcomics.com',
    url = 'http://urcomics.com',
    ext_modules = [mpoint_module]
    )
