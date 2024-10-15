run "unit" {
    description = "perform unit testing"
    command = "python3 -m unittest test/test_module.py"
    cwd = "../"
}

run "unit_docker" {
    description = "perform unit testing for docker feature"
    command = "python3 -m unittest test/test_module_docker.py"
    cwd = "../"
}

// run "lint" {
//     description = "lint test_module"
//     command = "pylint test_module.py"
//     cwd = "."
// }

run "unit-in-docker" {
run "unit-in-docker" {
    description = "perform unit testing in isolated env with docker"
    command = [
        "VERSION=$(python3 -c 'from myrunner._version import __version__; print(__version__)'); docker build  -f ./test/Dockerfile . --build-arg VERSION=$${VERSION} --tag myrunner:local",
        "docker run myrunner:local"
    ]
    cwd = "../"
}

run "unit_docker" {
    command = "python3 -m unittest test/test_module_docker.py"
    cwd = "../"
}