settings {
    description = "runlist for myrunner"
    interactive = false
}

run "clear" {
    description = "clean build dir"
    command = "rm -rf dist"
}

run "unit" {
    description = "test"
    command = "python3 -m unittest discover"
}

run "lint" {
    description = "run flake8 linter"
    command = "flake8"
}

run "lint_md" {
    description = "lint README using markdown lint docker"
    command = "docker run --rm -v $${PWD}:/lint pipelinecomponents/markdownlint mdl /lint --style all --warnings"
}

run "build" {
    description = "build myrunner"
    command = "python3 -m build"
}

run "install" {
    description = "install myrunner package on the host"
    command = "VERSION=$(python3 -c 'from myrunner._version import __version__; print(__version__)'); python3 -m pip install dist/myrunner-$${VERSION}-py3-none-any.whl --force-reinstall"
}

run "docker" {
    description = "build docker image"
    command = "VERSION=$(python3 -c 'from myrunner._version import __version__; print(__version__)'); docker build . --build-arg VERSION=$${VERSION} --tag myrunner:$${VERSION%%+*}"
}

run "all" {
    description = "run all runs"
    sequence = [
        clear,
        unit,
        lint,
        lint_md,
        build,
        install
    ]
}
