#!/usr/bin/env bash

####  CONFIGURABLES  #################################################

readonly DEBUG=1
readonly MAN_HELP=0    # 0=text help, 1=man help
readonly MAN_TYPE=1    # a command by man standards
readonly VERSION="0.3"

# Author metadata
readonly AUTHOR="Joseph Edwards VIII"
readonly AUTHOR_EMAIL="jedwards8th@gmail.com"


####  SELF  ##########################################################

# The 'self' command. Has special status.

# using man so prefix '-' with an escape '\'
readonly SELF_NAME="${SCRIPT} \- install mandelbrat or dependencies"

# script summary long as you like
readonly SELF_HELP="Install mandelbrat or just the dependencies."

# SELF_ARGS - if COMMANDS defined, then define empty: `SELF_ARGS=`
#SELF_ARGS="DEST POOP CRAP"

# SELF_OPTS_NOARG - singletons: ARGS ignored, and only 1st OPT parsed
SELF_OPTS_NOARG="h help v version"
SELF_OPTS_HELP=( \
    [h]="print help message" \
    [v]="print version information" \
    )

# SELF_OPTS - pairs short-long OPTS (ie, "t target" == -t, --target)
#SELF_OPTS="f foo"
#SELF_OPTS_HELP[f]="example self-as-command option"

# SELF_OPTARGS - string of positional option arguments
#SELF_OPTARGS[f]="BAR BAZ"


####  COMMANDS  ######################################################

# Command mode: first parameter commands can have ARGS and OPTS.
# If not defining commands then define empty: `COMMANDS=`

COMMANDS=( "install" "uninstall" "reinstall" )

CMD_HELP[install]="install app or resources"
CMD_OPTS[install]="d dep-only t target"

CMD_OPTARGS[t]="TARGET"

CMD_OPTS_HELP=( \
    [d]="install non-Pythonic system dependencies only" \
    [t]="install to TARGET directory (DEFAULT: ~/.mbrat)" \
    )

CMD_HELP[uninstall]="uninstall app only"
CMD_HELP[reinstall]="reinstall app only"


####  OPTIONAL MANPAGE  ##############################################

readonly FILES=
readonly ENVIRONMENT=
readonly EXIT_STATUS="Exits with status \$ERRNO."

#readonly EXAMPLE_01="${SCRIPT} skel /path/to/new/script"
#readonly EXAMPLE_02="${SCRIPT} fling -t -p poo dirt
#\(rs\"Phil Collins\(rs\" \(rs\"Batman and Robin\(rs\""
#readonly EXAMPLES="\&${EXAMPLE_01}\n\n\&${EXAMPLE_02}"

readonly BUGS=
readonly SEE_ALSO=


####  COMMAND FUNCTIONS  #############################################

# Must be named `_run_CMD` for each CMD in COMMANDS.
# Define each CMD function below. All your logic goes here.
# Use parsed CMD, OPTS[] with OPTARGS[opt], and ARGS[arg] here.

# Some globals, constants & defaults
readonly DEFINE_KEYS=( \
    COMMANDD ROOTD MAINF USRD CONFD BASHRC \
    )

INSTALL_PROG=
INSTALL_VER=
declare -A DEFINE
DEFAULT_INSTALL=true

# _run_self should always be defined and should minimally _print_help
function _run_self {
    _debug "\n_run_self:\n"
    _str_equal "$CMD" "self" && self_as_command && _exit_err
}

function self_as_command {

    if ! _is_empty "${ARGS[@]}"; then
        cmd_args=( ${CMD_ARGS[@]} )

        # NOTICE the use of 'eval' to get ARGS values
        for arg in "${cmd_args[@]}"; do
            eval val=${ARGS[$arg]}
            echo "${arg}: ${val}"
        done
    fi

    for opt in "${OPTS}"; do
        case $opt in
            h)
                _print_help
                _exit_err
                ;;
            v)
                echo "$SCRIPT $VERSION"
                _exit_err
                ;;
            *)
                _print_help
                _err; _exit_err
                ;;
        esac
    done
}


#### INSTALL subcommand ##############################################

function _run_install {

    # TODO
    echo "DEF_DEFINE: ${DEF_DEFINE[@]}"

    local install_rootd=

    for opt in "${OPTS}"; do
        case $opt in
            t)
                target=$(_trim "${OPTARGS[$opt]}")
                install_rootd=$(readlink -m "$target")
                [[ ! -e "$install_rootd" ]] && mkdir -p "$install_rootd"
                ;;
        esac
    done

    # TODO
    echo $install_rootd

    # Initialize some stuff
    init_cfg_vars
    make_define_py "$install_rootd"

}

function init_cfg_vars {
    # source bash cfg parser & read the manage cfg
    source "${SCRIPT_CFG_DIR}/read_ini.sh"
    read_ini "${SCRIPT_CFG_DIR}/${SCRIPT}.cfg" -p CFG

    # set $PROG from .cfg
    INSTALL_PROG=$CFG__PROG__PROG
    INSTALL_VER=$CFG__PROG__PROG_VER
}

function make_define_py {
    local install_rootd="$1"
    DEFINE[COMMANDD]="/usr/local/bin"

    if _is_empty "$install_rootd"; then
        DEFINE[ROOTD]="/home/${USER}/.${INSTALL_PROG}"
        DEFINE[MAINF]="${DEF_ROOTD}/${INSTALL_PROG}.py"
        DEFINE[USRD]="${DEF_ROOTD}/usr"
        DEFINE[CONFD]="/home/${USER}/.config/${INSTALL_PROG}"
    else
        DEFINE[ROOTD]="${install_rootd}"
        DEFINE[MAINF]="${install_rootd}/${INSTALL_PROG}.py"
        DEFINE[USRD]="${install_rootd}/usr"
        DEFINE[CONFD]="${install_rootd}/${INSTALL_PROG}rc.d"
    fi

    # generate 'mbrat/define.py' based on 'pacbrat.cfg' settings
    local define_py="${DEFINE[ROOTD]}/${INSTALL_PROG}/define.py"
    [ -e "$define_py" ] && rm "$define_py"

    define_str="\
MBRAT_PROG=\'${INSTALL_PROG}\'\n\
MBRAT_VER=\'${INSTALL_VER}\'\n\
MBRAT_PYVER=\'${CFG__REQUIRES__PYTHON_SHORT_VER}\'\n\
DEF_COMMANDD=\'${DEFINE[COMMANDD]}\'\n\
DEF_ROOTD=\'${DEFINE[ROOTD]}\'\n\
DEF_MAINF=\'${DEFINE[MAINF]}\'\n\
DEF_USRD=\'${DEFINE[USRD]}\'\n\
DEF_CONFD=\'${DEFINE[CONFD]}\'\n"

    printf $define_str > "$define_py"
}


#### EXAMPLE COMMAND FUNCTIONS  ######################################

# copy the skel directory and files to chosen destination
function copy_skel {
    dest="$1"
    skelname=`basename ${dest}`

    # default try to copy files out of ./skel directory
    src="$(readlink -m ./skel)"

    # if no 'skel' dir then use current directory (these files)
    [[ ! -d "${src}" ]] && src="$(readlink -m ./)"

    if [[ ! -f "${src}/${SCRIPT}" || ! -f "${src}/${SCRIPT}.sh" ]]; then
        _err; _exit_err "'${SCRIPT}' skel files not found."
    fi

    # now copy the files over
    echo "Copying ${src} directory to new directory ${dest} ..."

    [[ ! -d "${dest}" ]] && mkdir -p "${dest}"
    if [[ ! -d "${dest}" ]]; then
        _err; _exit_err "unable to create directory '${dest}'"
    fi

    cp "${src}/${SCRIPT}" "${dest}/${skelname}"
    if [[ ! -f "${dest}/${skelname}" ]]; then
        _err; exit_err "unable to copy '${SCRIPT}' to '${dest}/${skelname}'"
    fi

    cp "${src}/${SCRIPT}.sh" "${dest}/${skelname}.sh"
    if [[ ! -f "${dest}/${skelname}.sh" ]]; then
        _err; exit_err "unable to copy '${SCRIPT}.sh' to '${dest}/${skelname}.sh'"
    fi

    echo "SUCCESS!"
}

function _run_skel {
    eval dest=${ARGS[DEST]}
    copy_skel "$dest"

}

# example command function using options and option arguments
function _run_fling {

    verb="flings"
    noun1="love"
    noun2="flowers"

    # loop over OPTS + OPTARGS parsed, but *validate* here in `run_CMD`
    for opt in "${OPTS[@]}"; do
        case $opt in
            t)
                verb="tosses"
                ;;
            p)
                # NOTICE use of 'eval' to get OPTARGS array
                eval optargs=( ${OPTARGS[$opt]} )
                noun1="${optargs[0]}"
                noun2="${optargs[1]}"
                ;;
        esac
    done

    # this is what 'fling' cmd does...
    _debug "\n_run_fling:\n"

    # NOTICE use of 'eval' to get ARGS values
    eval src=${ARGS[SRC]}
    eval dest=${ARGS[DEST]}
    printf "${src} ${verb} ${noun1} and ${noun2} at ${dest}.\n"
}
