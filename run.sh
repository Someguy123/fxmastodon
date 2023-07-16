#!/usr/bin/env bash
################################################################
#                                                              #
#              Production runner script for:                   #
#                                                              #
#                  FxMastodon                                  #
#            (C) 2023  Someguy123   MIT X/11                   #
#                                                              #
#      Github Repo: https://github.com/Someguy123/fxmastodon   #
#                                                              #
################################################################

######
# Directory where the script is located, so we can source files regardless of where PWD is
######

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:${PATH}"
export PATH="${HOME}/.local/bin:${PATH}"

cd "$DIR"

[[ -f .env ]] && source .env || echo "Warning: No .env file found."

BOLD="" RED="" GREEN="" YELLOW="" BLUE="" MAGENTA="" CYAN="" WHITE="" RESET=""
if [ -t 1 ]; then
    BOLD="$(tput bold)" RED="$(tput setaf 1)" GREEN="$(tput setaf 2)" YELLOW="$(tput setaf 3)" BLUE="$(tput setaf 4)"
    MAGENTA="$(tput setaf 5)" CYAN="$(tput setaf 6)" WHITE="$(tput setaf 7)" RESET="$(tput sgr0)"
fi

# easy coloured messages function
# written by @someguy123
function msg() {
    # usage: msg [color] message
    if [[ "$#" -eq 0 ]]; then
        echo ""
        return
    fi
    if [[ "$#" -eq 1 ]]; then
        echo -e "$1"
        return
    fi

    ts="no"
    if [[ "$#" -gt 2 ]] && [[ "$1" == "ts" ]]; then
        ts="yes"
        shift
    fi
    if [[ "$#" -gt 2 ]] && [[ "$1" == "bold" ]]; then
        echo -n "${BOLD}"
        shift
    fi
    [[ "$ts" == "yes" ]] && _msg="[$(date +'%Y-%m-%d %H:%M:%S %Z')] ${@:2}" || _msg="${@:2}"

    case "$1" in
        bold) echo -e "${BOLD}${_msg}${RESET}" ;;
        [Bb]*) echo -e "${BLUE}${_msg}${RESET}" ;;
        [Yy]*) echo -e "${YELLOW}${_msg}${RESET}" ;;
        [Rr]*) echo -e "${RED}${_msg}${RESET}" ;;
        [Gg]*) echo -e "${GREEN}${_msg}${RESET}" ;;
        *) echo -e "${_msg}" ;;
    esac
}

case "$1" in
    update | upgrade)
        msg ts bold green " >> Updating files from Github"
        git pull
        msg ts bold green " >> Updating Python packages"
        pipenv update
        msg ts bold green " +++ Finished"
        echo
        msg bold yellow "Post-update info:"
        msg yellow "Please **become root**, and read the below additional steps to finish your update"

        msg yellow " - You may wish to update your systemd service files in-case there are any changes:"
        msg blue "\t cp -v *.service /etc/systemd/system/"
        msg blue "\t systemctl daemon-reload"

        msg yellow " - Please remember to restart the fxmastodon service AS ROOT like so:"
        msg blue "\t systemctl restart fxmastodon"
        ;;
    serve* | runserv*)
        # Override these defaults inside of `.env`
        : ${HOST='127.0.0.1'}
        : ${PORT='8285'}
        : ${GU_WORKERS='4'} # Number of Gunicorn worker processes
        : ${GU_TIMEOUT='600'} # Gunicorn request timeout

        pipenv run gunicorn -b "${HOST}:${PORT}" -w "$GU_WORKERS" --timeout "$GU_TIMEOUT" wsgi
        ;;
    *)
        msg bold red "Unknown command.\n"
        msg bold green "FxMastodon - (C) 2023 Someguy123"
        msg bold green "    Source: https://github.com/Someguy123/fxmastodon\n"
        msg green "Available run.sh commands:\n"
        msg yellow "\t update - Upgrade your FxMastodon installation"
        msg yellow "\t server - Start the production Gunicorn server"
        msg green "\nAdditional aliases for the above commands:\n"
        msg yellow "\t upgrade - Alias for 'update'"
        msg yellow "\t serve, runserver - Alias for 'server'"

        ;;
esac

msg

