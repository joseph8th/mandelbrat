CUSTOM_PREINSTALL=run_custom_preinstall
CUSTOM_INSTALL=run_custom_install
CUSTOM_POSTINSTALL=run_custom_postinstall
CUSTOM_PREUNINSTALL=
CUSTOM_UNINSTALL=run_custom_uninstall
CUSTOM_POSTUNINSTALL=


###################################
#           pre-install           #
###################################

function run_custom_preinstall {
    # generate 'mbrat/define.py' based on 'pacbrat.cfg' settings
    local define_py=./${PROG}/define.py
    [ -e $define_py ] && rm $define_py
    touch $define_py

    define_str="\
MBRAT_PROG=\'${PROG}\'\n\
MBRAT_VER=\'${CFG__PROG__PROG_VER}\'\n\
MBRAT_PYVER=\'${CFG__REQUIRES__PYTHON_SHORT_VER}\'\n\
DEF_COMMANDD=\'${DEF_COMMANDD}\'\n\
DEF_ROOTD=\'${DEF_ROOTD}\'\n\
DEF_MAINF=\'${DEF_MAINF}\'\n\
DEF_USRD=\'${DEF_USRD}\'\n\
DEF_CONFD=\'${DEF_CONFD}\'\n"

    printf $define_str >> $define_py
}


###################################
#             install             #
###################################

function run_custom_install {

    # first install the package the default '~/.${PROG}' dir
    if [[ "$PWD" != "$DEF_ROOTD" ]]; then

        # if not already in ~/.${PROG}, then setup.py ...
        if [ -e "./setup.py" ]; then
            echo "Running setup.py ..."
            python${CFG__INSTALL__PYTHON_SHORT_VER} setup.py install
        fi
        [[ ! "$?" ]] && _err && return

        # then change to install root dir
        cd ${DEF_ROOTD}
    fi

    # ask to install dependencies - WARNING experimental!
    local tmp_pwd="$PWD"
    local depends_ary=($CFG__REQUIRES__DEPENDS)
    for dep in $depends_ary; do
        echo "WARNING: '${dep}' is required."
        read -p "Should '${SCRIPT}' attempt experimental install? [y/N]: "
        [[ "$REPLY" != "y" ]] && _err && continue

        # source installer script and execute 'run_install_*' function
        TMPDIR=./tmp
        [[ ! -e "${TMPDIR}" ]] && mkdir $TMPDIR
        [[ ! -e "${SCRIPT}.d/${dep}.sh" ]] && _err && continue
        source ${SCRIPT}.d/${dep}.sh
        run_install_${dep}

        # switch back to working directory before continuing
        cd "$tmp_pwd"
    done

    [[ "$NOERR" != "0" ]] && return
}


###################################
#           post-install          #
###################################

# using only Python 2.7, for now ...
function check_req_pyver {

    local has_pyver=0
    local has_venv=0
    local req_venv_set=0

    for version in ${PYENV_DEF_ROOTD}/* 
    do
        [[ "$version" == *"$CFG__REQUIRES__PYTHON_VER}"* ]] && has_pyver=1
        [[ "$version" == *"$PROG"* ]] && has_venv=1
        [[ "$version" == *"* $PROG"* ]] && req_venv_set=1
    done

    # see if correct python version for virtualenv is installed
    if [[ "$has_pyver" -eq "0" ]]; then
        echo "'${PROG}' needs Python-${CFG__REQUIRES__PYTHON_VER}."
        read -p "Bootstrap Python-${CFG__REQUIRES__PYTHON_VER}? [y/N]: "
        [[ "$REPLY" != "y" ]] && _err && return

        echo "Installing Python-${CFG__REQUIRES__PYTHON_VER} ..."
        pyenv install ${CFG__REQUIRES__PYTHON_VER}
        [[ ! "$?" ]] && _err && return
    fi

    # see if correct virtualenv already set in pyenv
    [[ "$req_venv_set" -ne "0" ]] && return

    # see if virtualenv in pyenv but not set to local
    if [[ "$has_venv" -ne "0" ]]; then
       pyenv local $PROG
       [[ ! "$?" ]] && _err && return || return
    fi

    echo "'${PROG}' needs a 'pyenv' virtualenv."
    read -p "Initialize '${PROG}' virtualenv? [y/N]: " 
    [[ "$REPLY" != "y" ]] && _err && return

    # otherwise install a 'pybrat' virtualenv in ~/.pybrat
    echo "Installing virtualenv for '${PYENV_DEF_ROOTD}' ..."
    pyenv virtualenv ${CFG__REQUIRES__PYTHON_VER} ${PROG}
    pyenv local ${PROG}
}


function run_custom_postinstall {

    # install and config pyenv if user wants
    source ./${SCRIPT}.d/pyenv.sh
    check_req_pyenv

    # use pyenv to boostrap req py ver if user wants
    [[ "$NOERR" != "0" ]] && return || check_req_pyver
    [[ "$NOERR" != "0" ]] && return
}


###################################
#            uninstall            #
###################################

function run_custom_uninstall {

    if [ -e ${DEF_ROOTD} ]; then
        rm -rf "$DEF_ROOTD"
        [[ ! "$?" ]] && _err && return
    fi

    if [ -e ${DEF_COMMANDD}/${PROG} ]; then
        sudo rm "${DEF_COMMANDD}/${PROG}"
        [[ ! "$?" ]] && _err && return
    fi

}

