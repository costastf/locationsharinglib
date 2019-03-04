#!/usr/bin/env bash

# Needs to be sourced
# Sets up alias functions for the interface while keeping backwards compatibility with the old bash type

for command in $(ls _CI/scripts/ | cut -d'.' -f1 | grep -v "^_")
do
    eval "_$command() { if [ -f _CI/scripts/$command.py ]; then ./_CI/scripts/$command.py \"\$@\"; elif [ -f _CI/scripts/$command ]; then ./_CI/scripts/$command \"\$@\" ;else echo \"Command ./_CI/scripts/$command.py or ./_CI/scripts/$command not found\" ; fi }"
done

function _activate() {
    EXIT_CODE=false
    for path in '.venv/bin/activate' '_CI/files/.venv/bin/activate'
        do
            if [ -f "${path}" ]; then
                . "${path}"
                EXIT_CODE=true
                break
            fi
        done
    if [ "${EXIT_CODE}" = false ]; then
        echo Could not find virtual environment to activate
    fi
}
