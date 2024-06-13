# Envrionment variables feature
run "print_env_vars" {
    description = "echoing envs"
    command = "echo $${TEST_1} $${TEST_2} $${TEST_3}"
    envs = [ # if envs is missing or null, all envs will be provided, else only stated
        {
            name = "TEST_1"
            default = "Bye"
        },
        {
            name = "TEST_2"
            default = "world!"
        }
    ]
}

run "print_envs_if_not_stated" {
    description = "echo some env if envs are not stated"
    command = "echo $${TESTING_ENV}"
    envs = null
}

run "print_no_any_envs_except_system" {
    description = "echo no any vars except system"
    command = "printenv | grep -v PWD | grep -v /usr/bin/printenv | grep -v SHLVL; echo # omit return code"
    envs = []
}