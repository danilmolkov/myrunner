# Myrunner

## Introduction

Myrunner is a tool designed to facilitate declarative automation scripting.
It aims to streamline the process of creating and
running declarative scripts with ease.
This tool created due to lack of gooid declarative automation scripter tools.

### Why hcl

I think hcl is a good format made by Hashicorp. It is easier to read and understand.

## Features

- Declarative Runs: Define your automation scripts in a simple, declarative manner.
- Ease of Use: Simplified commands to run your scripts efficiently.

## Installation

To install Myrunner, clone this repository and install the required dependencies:

```bash
git clone https://github.com/danilmolkov/myrunner.git
cd myrunner
python -m pip install -r  requirements.txt
```

To start:

```bash
python -m myrunner.myrunner
```

To install Myrunner as package:

```bash
python3 -m build
VERSION=$(python3 -c 'from myrunner._version import __version__; print(__version__)')
python3 -m pip install dist/myrunner-$${VERSION}-py3-none-any.whl --force-reinstall
```

To start:

```bash
myrunner
```

## Blocks

### Settings

Block which defines settings which will be applied to all runs in this file.

### Run

The main block which describes a command which will be executed

```hcl
run "echo" {
    description = "Say hello"
    command = "echo $${MY_VAR}"
    envs = [ # if envs is missing or null, all envs will be provided, else only stated
        {
            name = "MY_VAR"
            default = "Hello World"
        },
    ]
}
```
