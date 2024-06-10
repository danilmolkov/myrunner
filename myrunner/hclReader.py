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
            # hcl syntax check
            self.obj = pygohcl.loads(path.read())

    # TODO: Create general schema
    __settings_schema = {
        "type": "object",
        "properties": {
            "interactive": {"type": "boolean"},
            "description": {"type": "string"}
        },
        "additionalProperties": False
    }

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

    def readSettings(self) -> dict:
        if self.obj.get('settings') is None:
            return {}
        if type(self.obj.get('settings')) == list:
            raise runnerExceptions.SchemaValiationError('test', 'settings block should be only one')
        try:
            validate(self.obj.get('settings'), self.__settings_schema)
        except exceptions.ValidationError as err:
            raise runnerExceptions.SchemaValiationError('test', err.message)
        return self.obj['settings']

    def readRuns(self) -> dict:
        for key, value in self.obj['run'].items():
            if '-' in key:
                logging.warn(f"using '-' is not suggested in run name: {key}")
            try:
                validate(value, self.__run_schema)
            except exceptions.ValidationError as err:
                raise runnerExceptions.SchemaValiationError(key, err.message)
        return self.obj['run']
