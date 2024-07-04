# Basic functionality.

run "first_run" {
    description = "prints hello world"
    command = "echo 'Hello World!'"
}

run "second_run" {
    description = "prints file content"
    command = "cat ./test/misc/testFile.txt"
}

run "run_script" {
    description = "run test script which"
    command = "bash ./test/scripts/runAndFail.sh"
}

run "heredoc_run" {
    description = "verify that heridoc is running"
    command = <<EOT
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

run "python_run" {
    description = "testing 'executable' feature"
    executable = "/usr/bin/python3"
    command = <<EOT
import itertools

def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

if __name__ == "__main__":
    example_list = [1, 2, 3]
    combinations = list(itertools.combinations(example_list, 2))
    print("Combinations:", combinations)
    flat_combinations = [item for sublist in combinations for item in sublist]
    print("Original array for sorting:", flat_combinations)
    sorted_combinations = quicksort(flat_combinations)
    print("Sorted array:", sorted_combinations)
EOT
}

run "command_array_type" {
    description = "test command as array"
    executable = "/usr/bin/python3"
    command = [
        "name='Billy'; print(f'Hi, my name is {name}')",
        "name='Garry'; print(f'Hi, and my name is {name}')"
    ]
}

run "command_array_type_failure" {
    description = "test command as array. But first command failed so the second command is not executed"
    command = [
        "function fail_function() { echo \"I'm failing\"; return 1; }; fail_function",
        "function success_function() { echo \"I shouldn't start\" }; success_function"
    ]
}
