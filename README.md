Overview
========

MandelBrat (`mbrat`) is a Linux explorer for multiple-precision Mandelbrot Set profiles.

Note
----

This version is NOT fully functional. Crypto functionality has not been implemented here. The crypto SPIs are being developed as standalone services for future compatibility with other crypto APIs. Expect all this in v1.0-alpha.

IOW, this version is a pared-down and profile-driven Mandelbrot Set explorer. Don't expect fancy graphics (yet).


Installation
============

Requirements
------------

- GNU/Linux operating system with Gtk+ 3 libraries
- Python 2.7
- `easy_install-2.7` installed to your `python2.7` path
- [git](http://git-scm.com/download/linux) - for installation and updates
- [gmp](http://gmplib.org/) >= 5.0.x
- [mpfr](http://www.mpfr.org/mpfr-current/#download) >= 3.1.0
- [mpc]() >= 1.0

* NOTE: Required Python packages will be installed by the `bratman` script using `easy_install-2.7`.

Procedure
---------

Execute the following statements in your shell (do _not_ type the prompt, `$`) :

    $ git clone https://github.com/joseph8th/mandelbrat.git
    $ cd mandelbrat
    $ ./bratman -i

Install Help
------------

Instead of last step above, just execute:

    $ ./bratman -h

Version Notes
-------------

- This version of `bratman` here has limited function. Future versions will be generalized and forked to a side project to allow configured deployment of Pythonic "Brats" to further enhance project deployment using standard tools.
- This version of `mbrat` would like install a 'usr' configuration tree in your `$HOME/.config/` directory, and itself in a `$HOME/.mbrat directory`, with an executable in your `/usr/local/bin`. Don't worry... I'll fix that, soon.


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