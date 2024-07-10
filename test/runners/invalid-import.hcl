import {
    imported = "./invalid-name.hcl"
}

run "usual_run" {
    command = "echo \"I'm usual run\""
}

run "import_sequence" {
    sequence = [
        imported.imported_sequence,
        usual_run
    ]
}