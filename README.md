Overview
========

MandelBrat (`mbrat`) is a Linux explorer for Mandelbrot Set-based multiprecision fractal key crytographic services -- called SPIs to follow the Java Security API convention. Both the Mandelbrot Set explorer and crypto functionality may be accessed either from the command line, or via built-in GUI (Gtk+ 3).

Note
----

This version is NOT fully functional. Crypto functionality has not been implemented here. The crypto SPIs are being developed as standalone services for future compatibility with other crypto APIs. Expect all this in v1.0-alpha.

IOW, this version is a pared-down and profile-driven Mandelbrot Set explorer. Don't expect fancy graphics (yet). And you won't find the crypto functions implemented here. :evilgrin:


Installation
============

Version Notes
-------------

- `setup.py` currently has limited use to building the extension module. Specifically, `setup.py install` will fail.
- `mbrat` would like install a 'usr' configuration tree in your `$HOME/.config/` directory, and itself in a `$HOME/.mbrat directory`, with an executable in your `/usr/local/bin`
- There is no systemwide install because this will eventually be a crypto program. Users have their own 'usr' trees, and crypto will be provided for MandelBrat as an advanced exploration of released SPIs of the `mbrat` API.

Requirements
------------

- GNU/Linux operating system with Gtk+ 3 libraries
- Python 2.7
- `easy_install-2.7` installed to your `python2.7` path
- [git](http://git-scm.com/download/linux)
- [gmp](http://gmplib.org/) >= 5.0.x
- [mpfr](http://www.mpfr.org/mpfr-current/#download) >= 3.1.0
- [mpc]() >= 1.0

Required Python packages will be installed by the `install` script using `easy_install-2.7`.

Procedure
---------

Execute the following statements in your shell (do _not_ type the prompt, `$`) :

    $ git clone https://github.com/joseph8th/mandelbrat.git
    $ cd mandelbrat
    $ ./install

Install Help
------------

Instead of last step above, just execute:

    $ ./install -h


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

0.2 (2014-02-01)
-----------------

- Eliminated both C and C++ extension modules and switched to `gmpy2` Python package to interface with listed
  required multiple-precision libraries.

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