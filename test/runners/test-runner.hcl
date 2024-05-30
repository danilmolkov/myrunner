# Basic functionality.

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

run "heredoc_run" {
    description = "verify that heridoc is running"
    execute = <<EOT
echo $(basename $(pwd))
greeting="hello world!"
echo $${greeting:6}
x=1
while [ $x -le 5 ]; do
    echo -n $${x}
    ((x=x+1))
done
echo
EOT
}