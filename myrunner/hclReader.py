import pygohcl
import logging
from jsonschema import validate
from jsonschema import exceptions
import os.path

import myrunner.common.runnerExceptions as runnerExceptions

run_schema = {
    "type": "object",
    "properties": {
        "description": {"type": "string"},
        "execute": {"type": "string"},
    },
    "required": ["description", "execute"],
    "additionalProperties": False
}


def readRuns(file: str) -> dict:
    if not os.path.exists(file):
        raise runnerExceptions.FileNotFound(file)
    with open(file, 'r') as file:
        try:
            obj = pygohcl.loads(file.read())['run']
        except KeyError:
            raise exceptions.SchemaError('runs are missing')
    for key, value in obj.items():
        if '-' in key:
            logging.warn(f"using '-' is not suggested in run name: {key}")
        validate(value, run_schema)
    return obj
