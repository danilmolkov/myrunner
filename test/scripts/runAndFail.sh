#!/usr/bin/bash

function main() {

    for i in {1..3}; do
        echo "test stdout"
        >&2 echo "error"
        sleep 1
    done

    exit 1

}

main