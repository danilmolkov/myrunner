
run "imported_run" {
    command = "echo 'Hello World!'"
}

run "imported_sequence" {
    sequence = [
        imported_run,
    ]
}