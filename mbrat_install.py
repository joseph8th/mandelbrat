#!/usr/bin/env python

import os
import mbrat.installer as installer

# installer root dir is wherever THIS file 'mbrat_install.py' is ...
if __name__=="__main__":
    installer.main(os.path.dirname(os.path.realpath(__file__)))
