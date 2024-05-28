# Locals import.

locals {
    test_string = "I am local"
}

run "string_import" {
    description = "import string from local and prints it"
    execute = "echo 'Hello World!'"
}

