import pygohcl
import logging
from jsonschema import validate
from jsonschema import exceptions
import os.path

import myrunner.common.runnerExceptions as runnerExceptions

class HclReader:

    def __init__(self, path: str) -> None:
        if not os.path.exists(path) or os.path.isdir(path):
            raise runnerExceptions.FileNotFound(path)
        with open(path, 'r') as path:
            try:
                self.obj = pygohcl.loads(path.read())
                self.obj['run']
            except KeyError:
                raise exceptions.SchemaError('runs are missing')

    __run_schema = {
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

    def getRuns(self) -> dict:
        for key, value in self.obj['run'].items():
            if '-' in key:
                logging.warn(f"using '-' is not suggested in run name: {key}")
            try:
                validate(value, self.__run_schema)
            except exceptions.ValidationError as err:
                raise runnerExceptions.SchemaValiationError(key, err.message)
        return self.obj['run']
