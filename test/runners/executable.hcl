# TODO: settings feature

settings {
    executable = "/usr/bin/python3.12"
    # working_dir = null  - current
    # working_dir = "." - place from which called
    # other = any string
}


run "python" {
    execute = <<EOT
import sys
print(f'Hello from Python {sys.version_info.major}.{sys.version_info.minor} :)')
EOT
}