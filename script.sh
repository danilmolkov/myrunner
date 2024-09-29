#!/bin/bash

ctrlc_received=0

function handle_ctrlc()
{
    echo
    if [[ $ctrlc_received == 0 ]]
    then
        echo "I'm hmmm... running. Press Ctrl+C again to stop!"
        ctrlc_received=1
    else
        echo "It's all over!"
        exit
    fi
}

# trapping the SIGINT signal
trap handle_ctrlc SIGINT
trap handle_ctrlc SIGTERM

while true
do
    >&2 echo "stderr"
    echo "stdout"
    sleep 2
done