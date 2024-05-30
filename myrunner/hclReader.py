import pygohcl
import logging
from jsonschema import validate
from jsonschema import exceptions
import os.path

import myrunner.common.runnerExceptions as runnerExceptions

class HclReader:

    def __init__(self, path: str) -> None:
        if not os.path.exists(path):
            raise runnerExceptions.FileNotFound(path)
        with open(path, 'r') as path:
            try:
                self.obj = pygohcl.loads(path.read())['run']
                print(self.obj)
            except KeyError:
                raise exceptions.SchemaError('runs are missing')

    run_schema = {
        "type": "object",
        "properties": {
            "description": {"type": "string"},
            "execute": {"type": "string"},
            "envs": {
                "type": ["null", "array"],
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "default": {
                        "type": "string"
                    },
                },
                "required": ["name"],
                "additionalProperties": False
            }
        },
        "required": ["execute"],
        "additionalProperties": False
    }

    def readRuns(self) -> dict:
        for key, value in self.obj.items():
            if '-' in key:
                logging.warn(f"using '-' is not suggested in run name: {key}")
            try:
                validate(value, self.run_schema)
            except exceptions.ValidationError as err:
                raise runnerExceptions.SchemaValiationError('test', err.message)
        return self.obj
