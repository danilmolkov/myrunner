run "test" {
    description = "test"
    execute = "python3 -m unittest discover"
}

run "build" {
    description = "build myrunner"
    execute = "python3 -m build"
}

run "install" {
    description = "install myrunner package on the host"
    execute = "python3 -m pip install dist/myrunner-0.0.1-py3-none-any.whl --force-reinstall"
}
