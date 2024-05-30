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
    execute = "VERSION=$(python3 -c 'from myrunner._version import __version__; print(__version__)'); python3 -m pip install dist/myrunner-$${VERSION}-py3-none-any.whl --force-reinstall"
}

run "print_env_var" {
    description = "print TEST_1 env var value"
    execute = "echo $${TEST_1} $${TEST_2} $${TEST_3}"
    envs = [
        {
            name = "TEST_1"
            default = "hello"
        },
        {
            name = "TEST_2"
            default = "world!"
        }
    ]
}

run "print_envs_if_not_stated" {
    description = "echo some env if envs are not stated"
    execute = "echo $${TESTING_ENV}"
}


run "print_no_any_envs" {
    description = "echo no any vars except system"
    execute = "printenv | grep -v PWD | grep -v /usr/bin/printenv | grep -v SHLVL; echo # omit return code"
    envs = []
}

locals {
    test_string = "I am local"
}

run "string_import" {
    description = "import string from local and prints it"
    execute = "echo ${locals.test_string}"
}