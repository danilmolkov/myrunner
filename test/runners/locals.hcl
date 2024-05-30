// TODO: Add locals feature support

locals {
    test_string = "I am local"
}

run "string_import" {
    description = "import string from local and prints it"
    execute = "echo ${local.test_string}"
}

