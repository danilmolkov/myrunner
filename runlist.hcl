run "clear" {
    description = "clean build dir"
    execute = "rm -rf dist"
}

run "unit" {
    description = "test"
    execute = "python3 -m unittest discover"
}

run "lint" {
    description = "run flake8 linter"
    execute = "flake8"
}

run "lint_md" {
    description = "lint README using markdown lint docker"
    execute = "docker run --rm -v $${PWD}:/lint pipelinecomponents/markdownlint mdl /lint --style all --warnings"
}

run "build" {
    description = "build myrunner"
    execute = "python3 -m build"
}

run "install" {
    description = "install myrunner package on the host"
    execute = "VERSION=$(python3 -c 'from myrunner._version import __version__; print(__version__)'); python3 -m pip install dist/myrunner-$${VERSION}-py3-none-any.whl --force-reinstall"
}
