############################
#### Config for 'pyenv' ####
############################

#### Install script (bash) defaults. ####

#[pyenv]
PYENV_DEF_ROOTD=/home/${USER}/.pyenv
PYENV_DEF_PYD=/home/${USER}/.pyenv/versions
PYENV_DEF_VENVD=/home/${USER}/.pyenv/versions


# Configure the user's shell script if they want.
function _config_shrc_pyenv {

    echo; read -p "Configure 'pyenv' for your shell? [y/N]: "
    if [[ "$REPLY" != "y" ]]; then
        printf "\n==> ERROR: 'pyenv' needs to be configured to work!\n"
        echo "Read the 'README.md' in '${PYENV_DEF_ROOTD}'."
	_err; return
    fi

    local sh=
    echo; read -p "Using: [0] .bashrc, OR [1] .bash_profile ? "
    case $REPLY in
        0)
            sh=".bashrc"
            ;;
        1)
            sh=".bash_profile"
            ;;
        *)
	    _err; return
            ;;
    esac

    # append pretty 'pyenv' env vars to the chosen shell cfg
    printf "\n# 'pyenv' environment configuration\n" >> ${HOME}/${sh}
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ${HOME}/${sh}
    echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ${HOME}/${sh}
    echo 'eval "$(pyenv init -)"' >> ${HOME}/${sh}

    # perform the config for this shell session
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"

    echo '==> DONE! You may need to restart your shell. Type `exec $SHELL`.'
    printf "(On uninstall, delete 'pyenv' section from '${HOME}/${sh}'.)\n\n"

    return
}



# Check if 'pyenv' and plugins are installed and if not, install.
function _check_req_pyenv {

    # see if pyenv already installed and return if so
    #search_path "$PYENV_DEF_ROOTD"
    #[[ "$FIND_PATH" == "0" ]] && return
    [[ ! -z "$PYENV_ROOT" && -d "$PYENV_ROOT" ]] && return
    
    # check for .pyenv directory in case installed but not config'd
    if [ -e "$PYENV_DEF_ROOTD" ]; then
        echo "==> ERROR: 'pyenv' installed but not configured."
        echo "Did you read the 'README.md' in '${PYENV_DEF_ROOTD}'?"
        _config_shrc_pyenv
	_err; return
    fi

    # good to install here ...
    echo "==> This version of PyBrat requires 'pyenv'."
    read -p "Use 'git' to clone and install 'pyenv' to defaults? [y/N]: "
    [[ "$REPLY" != "y" ]] && _err && return
    
    # ... so clone it all from github
    echo
    git clone git://github.com/yyuu/pyenv.git $PYENV_DEF_ROOTD
    if [ ! -e "$PYENV_DEF_ROOTD" ]; then
        echo "==> ERROR: 'pyenv' did not install correctly."
	_err; return
    fi
    echo
    git clone git://github.com/yyuu/pyenv-virtualenv.git ${PYENV_DEF_ROOTD}/plugins/pyenv-virtualenv
    if [ ! -e "${PYENV_DEF_ROOTD}/plugins/pyenv-virtualenv" ]; then
        echo "==> ERROR: 'pyenv-virtualenv' did not install correctly."
	_err; return
    fi

    # config user's shell
    _config_shrc_pyenv
    return
}

