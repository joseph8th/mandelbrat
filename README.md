Overview
========

MandelBrat (`mbrat`) is a Linux explorer for multiple-precision Mandelbrot Set profiles.

Note
----

This version is NOT fully functional. Crypto functionality has not been implemented here. The crypto SPIs are being developed (slowly) with an eye toward making them standalone services for future compatibility with other crypto APIs. Expect all this in v1.0.

IOW, this version is a pared-down and profile-driven Mandelbrot Set explorer. Don't expect fancy graphics (yet).


Installation
============

Requirements
------------

Because `mbrat` uses multiple-precision complex and floating-point numbers, it requires:

- GNU/Linux operating system with Gtk+ 3 libraries
- [gmp](http://gmplib.org/) >= 5.0.x
- [mpfr](http://www.mpfr.org/mpfr-current/#download) >= 3.1.0
- [mpc](http://www.multiprecision.org/index.php?prog=mpc&page=download) >= 1.0
- [cairo](http://cairographics.org/download/) - for GUI

In addition there are the Pythonic requirements:

- Python-2.7 installed _system-wide_ (ever try to install `GObject Introspection` in a `virtualenv`?)
- `setuptools` - to use `easy_install-2.7`
- `pypng` - we need to do `import png`
- `gmpy2` - we need to do `import gmpy2`

Installation
------------

Execute the following statements in your shell:

    $ git clone https://github.com/joseph8th/mandelbrat.git
    $ cd mandelbrat

MandelBrat may now be executed directly as a Python script:

    $ ./mbrat.py -h

Or install in-place, if you like:

    $ sudo ln -s ./mbrat.py /usr/local/bin/mbrat
    $ mbrat -h


Usage
=====

    $ mbrat COMMAND [OPTION...]

MandelBrat may be used either from your shell (the command line terminal of your Linux OS) or via a graphical user interface (GUI).

To run MandelBrat from the command line, execute one of the following:

    $ mbrat --help
    $ mbrat COMMAND --help

To run the MandelBrat GUI, run the following command:

    $ mbrat gui


Changelog
=========

0.2a (2015-01-17)
-----------------

- Eliminated installer rubbish - this is a dev toy, not a product, so users will just have to bite the bullet and install dependencies directly.

0.2 (2014-02-01)
-----------------

- Eliminated both C and C++ extension modules and switched to `gmpy2` Python package to interface with listed required multiple-precision libraries.

0.1h (2013-10-16)
-----------------

- Rewrote the MPoint C++ class as pure importable C functions.
- Without C++ object dependency, Boost libs no longer needed, so eliminated.

0.1h (2013-05-12)
-----------------

- Fine-tuned `installer` module to provide more comprehensive installation functions.
- Wrote `sanity_check` method for `ConfigManager` class to ensure `usr` tree installed correctly.
- Debugged the whole program after all the refactoring and tuning between versions `g` and `h`.
- Completed `clogger` function to route program text output to `console` or `stdout`.
- Removed `usr` tree (permanently) and `tests` (temporarily) from distributed (Git) version.

0.1g (2013-04-14)
-----------------

- Restructured `usr` directory structure and fine-tuned related `.cfg` files.
- Wrote `setup.py` to build and install exension modules (instead of `make` or `bjam`)
- Completed `installer` package to install mbrat to the user $HOME.

Previous Verions
----------------

- (0.1a-0.1f) Development versions only did their thing on my machine. See the Git site for more information.
- (0.0) Prototyped using MATLAB GUI.


Author
======

    Joseph E. Edwards VIII
    joseph8th@notroot.us
    http://notroot.us


Website
=======

https://github.com/joseph8th/mandelbrat