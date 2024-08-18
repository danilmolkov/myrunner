#!/usr/bin/myrunner -f
settings {
    description = "runlist for myrunner"
    interactive = false
}

locals {
    bird = "awebo"
    number = "one"
    cat = "meow"
    myrunner_version = "$(python3 -c 'from myrunner._version import __version__; print(__version__)')"
}

import {
    unit = "./test/unit.hcl"
}

run "clear" {
    description = "clean build dir"
    command = "rm -rf dist"
}

run "lint" {
    description = "run flake8 linter"
    // sequence = [
    //     unit.lint
    // ]
    command = ["flake8",
               "pylint ./myrunner"
            ]
}

run "lint_md" {
    description = "lint README using markdown lint docker"
    command = "docker run --rm -v $${PWD}:/lint pipelinecomponents/markdownlint mdl /lint --style all --warnings"
    cwd = "."
}

run "build" {
    description = "build myrunner"
    command = "python3 -m build"
    cwd = "."
}

run "install" {
    description = "install myrunner package on the host"
    command = "VERSION=${local.myrunner_version}; python3 -m pip install dist/myrunner-$${VERSION}-py3-none-any.whl --force-reinstall"
    cwd = "."
}

run "docker" {
    description = "build docker image"
    command = "VERSION=${local.myrunner_version} && docker build  -f ./test/Dockerfile . --build-arg VERSION=$${VERSION} --tag registry.gitlab.com/danilmolkov/myrunner:stable"
}

run "copy_from_local_to_bin" {
    description = "copy myrunner executable to /usr/bin"
    command = [
        "sudo cp /home/dmolkov/.local/bin/myrunner /usr/bin/",
        "test -e /usr/bin/myrunner"
    ]
}

run "all" {
    description = "execute all runs"
    sequence = [
        clear,
        unit.unit,
        lint,
        lint_md,
        build,
        install
    ]
}

run "awebo" {
    description = "Bird says ${local.bird} ${local.number}"
    command = "echo '( * |> ${local.bird}| = ^ ^ = ${local.cat}'"
}

run "squild" {
    description = "turn on/off squid container"
    command = <<EOT
# Replace 'container_name' with the name of your Docker container
CONTAINER_NAME="squid"

# Check if the container is running
CONTAINER_STATUS=$(docker ps --filter "name=$CONTAINER_NAME" --filter "status=running" -q)

if [ -n "$CONTAINER_STATUS" ]; then
    echo "Stopping container: $CONTAINER_NAME"
    docker stop $CONTAINER_NAME 1> /dev/null
else
    echo "Starting container: $CONTAINER_NAME"
    docker start $CONTAINER_NAME 1> /dev/null
fi
EOT
}