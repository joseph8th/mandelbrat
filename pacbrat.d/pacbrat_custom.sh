CUSTOM_PREINSTALL=
CUSTOM_INSTALL=_run_custom_install
CUSTOM_POSTINSTALL=_run_custom_postinstall
CUSTOM_PREUNINSTALL=
CUSTOM_UNINSTALL=_run_custom_uninstall
CUSTOM_POSTUNINSTALL=


function _run_custom_install {

    # then we can install the default '~/.${CFG__PROG__PROG}' dir
    if [[ "$PWD" != "$CFG__INSTALL__DEF_ROOTD" ]]; then

        # if not already in ~/.${CFG__PROG__PROG}, then setup.py ...
        if [ -e "./setup.py" ]; then
            echo "Running setup.py ..."
            python${CFG__INSTALL__PYTHON_SHORT_VER} setup.py install
        fi

        [ $? ] && _err && return

        # then change to install root dir
        cd ${CFG__INSTALL__DEF_ROOTD}
    fi
}


###################################
#           post-install           #
###################################

# using only Python 2.7, for now ...
function _check_req_pyver {

    local pyvers="$(pyenv versions)"

    # see if correct python version for virtualenv is installed
    if [[ "$pyvers" != *"$CFG__PROG__PYTHON_VER"* ]]; then
        echo "'${CFG__PROG__PROG} needs Python-${CFG__REQUIRES__PYTHON_VER}."
        read -p "Bootstrap Python-${CFG__REQUIRES__PYTHON_VER}? [y/N]: "
        [[ "$REPLY" != "y" ]] && _err && return

        echo "Installing Python-${CFG__REQUIRES__PYTHON_VER} ..."
        pyenv install ${CFG__REQUIRES__PYTHON_VER}
        [[ "$?" ]] && _err && return
    fi

    # see if correct virtualenv already set in pyenv
    [[ "$pyvers" == *"* $CFG__PROG__PROG "* ]] && return

    # see if virtualenv in pyenv but not set to local
    if [[ "$pyvers" == *"$CFG__PROG__PROG"* ]]; then
       pyenv local $CFG__PROG__PROG
       [[ "$?" ]] && _err && return || return
    fi

    echo "'${CFG__PROG__PROG}' needs a 'pyenv' virtualenv."
    read -p "Initialize '${CFG__PROG__PROG}' virtualenv? [y/N]: " 
    [[ "$REPLY" != "y" ]] && _err && return

    # otherwise install a 'pybrat' virtualenv in ~/.pybrat
    echo "Installing virtualenv for '${PYENV_DEF_ROOTD}' ..."
    pyenv virtualenv ${CFG__REQUIRES__PYTHON_VER} ${CFG__PROG__PROG}
    pyenv local ${CFG__PROG__PROG}
}


function _run_custom_postinstall {

    # install and config pyenv if user wants
    source ./${SCRIPT}.d/pyenv.sh
    _check_req_pyenv

    # use pyenv to boostrap req py ver if user wants
    [[ "$NOERR" != "0" ]] && return || _check_req_pyver
    [[ "$NOERR" != "0" ]] && return

    # generate 'mbrat/define.py' based on 'pacbrat.cfg' settings
    local define_py=./${CFG__PROG__PROG}/define.py
    [ -e $define_py ] && rm $define_py

    $define_str="\
MBRAT_PROG='${CFG__PROG__PROG}'\n\
MBRAT_VER='${CFG__PROG__PROG_VER}'\n\
MBRAT_PYVER='${CFG__REQUIRES__PYTHON_SHORT_VER}'\n\
DEF_COMMANDD='${CFG__INSTALL__DEF_COMMANDD}'\n\
DEF_ROOTD='${CFG__INSTALL__DEF_ROOTD}'\n\
DEF_MAINF='${CFG__INSTALL__DEF_MAINF}'\n\
DEF_USRD='${CFG__INSTALL__DEF_USRD}'\n\
DEF_CONFD='${CFG__INSTALL__DEF_CONFD}'\n"

    touch $define_py
    printf $define_str >> $define_py
}


function _run_custom_uninstall {

    if [ -e ${CFG__INSTALL__DEF_ROOTD} ]; then
        rm -rf "$CFG__INSTALL__DEF_ROOTD"
        [ $? ] && _err && return
    fi

    if [ -e ${CFG__INSTALL__DEF_COMMANDD}/${CFG__PROG__PROG} ]; then
        sudo rm "${CFG__INSTALL__DEF_COMMANDD}/${CFG__PROG__PROG}"
        [ $? ] && _err && return
    fi

}

