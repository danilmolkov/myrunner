function __myrunner_debug_print {
    if [[ ! -z $__MYRUNNER_DEBUG ]]; then
        echo $1
    fi
}

function __myrunner_comp_preparation {
    if [[ ! -f '/usr/bin/python' && ! -f '/usr/bin/python3' ]]; then
        >&2 echo "python executables (/usr/bin/python or /usr/bin/python3) not found"
        return -1
    fi
    return 0
}

function __myrunner_completions {
    __myrunner_debug_print "starting __myrunner_completions"
    if ! __myrunner_comp_preparation ; then
        __myrunner_debug_print "__myrunner_comp_preparation failed"
        return -1
    fi
    local __myrunner_filepath="runlist.hcl"

    for (( i=0; i<((${#COMP_WORDS})); i++ ))
    do
        case ${COMP_WORDS[$i]} in
            -f)
                __myrunner_debug_print "local path used"
                __myrunner_filepath=${COMP_WORDS[$((i+1))]}
                ;;
            -u)
                __myrunner_debug_print "user path used"
                __myrunner_filepath="${HOME}/.runlist.hcl"
                break
                ;;
            *)
                ;;
        esac
    done

    # no auto-indentation in case of opt args
    if [[ ${COMP_WORDS[-1]} =~ ^-.* ]]; then
        __myrunner_debug_print "no auto-indentation in case of opt args"
        return
    fi

    if [[ ${COMP_WORDS[-2]} == "-f" ]]; then
        COMPREPLY=($(compgen -o plusdirs -f -X '!*.hcl' -- "${COMP_WORDS[COMP_CWORD]}"))
        if [[ ${COMPREPLY: -3} != "hcl" && ! -z "$COMPREPLY" ]]; then
            COMPREPLY+="/"
        fi
        __myrunner_filepath="$COMPREPLY"
        return
    fi

    __myrunner_debug_print "__myrunner_filepath ${__myrunner_filepath}"
    local LIST=$(python3 ~/.local/bin/myrunner --complete ${__myrunner_filepath})
    __myrunner_debug_print "LIST:${LIST}"
    COMPREPLY=($(compgen -W "$LIST" "${COMP_WORDS[-1]}"))

    __myrunner_debug_print "__myrunner_completions finising"

}
# __myrunner_completions
complete -o default -o nospace -F __myrunner_completions myrunner