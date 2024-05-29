run "clear" {
    description = "clean build dir"
    execute = "rm -rf dist"
}

run "test" {
    description = "test"
    execute = "python3 -m unittest discover"
}

run "lint" {
    description = "run flake8 linter"
    execute = "flake8"
}

run "build" {
    description = "build myrunner"
    execute = "python3 -m build"
}

run "install" {
    description = "install myrunner package on the host"
    execute = "python3 -m pip install dist/myrunner-0.2.0-py3-none-any.whl --force-reinstall"
}