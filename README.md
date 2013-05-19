OVERVIEW
========

MandelBrat (`mbrat`) is a Linux explorer for Mandelbrot Set-based multiprecision fractal key crytographic services -- called SPIs to follow the Java Security API convention. Both the Mandelbrot Set explorer and crypto functionality may be accessed either from the command line, or via built-in GUI (Gtk+ 3).

Note
----

This version is NOT fully functional. Crypto functionality has not been implemented here. The crypto SPIs are being developed as standalone services for future compatibility with other crypto APIs. Expect all this in v1.0-alpha.

IOW, this version is a pared-down and profile-driven Mandelbrot Set explorer. Don't expect fancy graphics (yet). And you won't find the crypto functions implemented here. :evilgrin:


SYSTEM REQUIREMENTS
===================

During the development versions, MandelBrat will rely on Boost (C++) extensions to Python 2.7. For GCC to compile these, you're gonna want to have Boost::Multiprecision and Boost::Python libraries on your include path.

Plan is to do away with these... somehow... by the time v0.2 is released.

MandelBrat also relies on Gtk+ 3. Sorry stick-in-the-muds... time for an upgrade.


INSTALLATION
============

Version Notes
-------------

- `setup.py` currently has limited use to building the extension module. Dependencies will *not* be satisfied by Distutils.
- `mbrat` would like install a 'usr' configuration tree in your `$HOME/.config/` directory, and itself in a `$HOME/.mbrat directory`, with an executable in your `/usr/local/bin`
- There is no systemwide install because this will eventually be a crypto program. Users have their own 'usr' trees, and crypto will be provided for MandelBrat as an advanced exploration of released SPIs of the `mbrat` API. Get it? The fun Mandelbrot Set you know and love makes `mbrat` possible, but the crypto functions can't be a *toy*

Requirements
------------

- GNU/Linux operating system with Gtk+ 3 libraries
- `[git](http://git-scm.com/download/linux)` and `python2.7` are required to install and run
- `[boost](http://www.boost.org/users/download/)`, `[mpfr](http://www.mpfr.org/mpfr-current/#download)`, and `[gmp](http://gmplib.org/)` libraries are required on your include path
- `[PyPNG](http://pythonhosted.org/pypng/index.html)` Python package is required to run

Install Procedure
-----------------

Execute the following statements in your shell (do _not_ type the prompt, `$`) ::

    $ git clone https://github.com/joseph8th/mandelbrat.git
    $ cd mandelbrat
    $ ./mbrat-install

Install Help
------------

Instead of last step above, just execute::

    $ ./mbrat-install -h


USAGE
=====

mbrat command [options]

MandelBrat may be used either from your shell (the command line terminal of your Linux OS) or via a graphical user interface (GUI) if Gtk+ 3.0 is installed on your computer.

To run MandelBrat from the command line, run the following and then choose a command::

    $ mbrat --help

To run the MandelBrat GUI, run the following command::

    $ mbrat gui 


COMMANDS
========

Run the following to for a list of commands::

  $ mbrat --help

Run the following for help with a particular `COMMAND`::

  $ mbrat COMMAND --help


CHANGELOG
=========

0.1h (2013-05-12)
-----------------

- Fine-tuned `installer` package to provide more comprehensive installation functions.
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


AUTHOR
======

Joseph E. Edwards VIII
joseph8th@notroot.us
http://notroot.us


WEBSITE
=======

https://github.com/joseph8th/mandelbrat