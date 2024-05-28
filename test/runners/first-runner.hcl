# First runner. Basic functionality.

run "first_run" {
    description = "prints hello world"
    execute = "echo 'Hello World!'"
}

run "second_run" {
    description = "prints file content"
    execute = "cat ./test/misc/testFile.txt"
}

run "run_script" {
    description = "run test script which"
    execute = "bash ./test/scripts/runAndFail.sh"
}

