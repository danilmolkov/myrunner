run "run_successful" {
    command = "function success_function() { echo \"Success!\"; }; success_function"
}

run "run_unsuccessful" {
    command = "function fail_function() { echo \"Failing :(\"; return 1; }; fail_function"
}

run "sequence_successful" {
    sequence = [
        run_successful,
        run_successful
    ]
}

run "sequence_unsuccessful" {
    sequence = [
        run_successful,
        run_unsuccessful,
        run_successful
    ]
}

run "run_sequence_of_sequence" {
    sequence = [
        sequence_successful,
        sequence_unsuccessful,
        sequence_successful,
    ]
}
run "run_sequence_with_invalid_run" {
    sequence = [
        sequence_successful,
        some_invalid_name,
        sequence_successful,
    ]
}