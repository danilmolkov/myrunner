import pygohcl
import logging
from jsonschema import validate, exceptions
import os.path

import myrunner.common.runnerExceptions as runnerExceptions

class HclReader:
    def __init__(self, path: str) -> None:
        if not os.path.exists(path) or os.path.isdir(path):
            raise runnerExceptions.FileNotFound(path)
        with open(path, 'r') as file:
            # hcl syntax check
            self.obj = pygohcl.loads(file.read())
        # importing runlists
        self.obj['__imported'] = {}
        if 'import' in self.obj:
            from os import path as ph
            runfile_dir = ph.dirname(ph.abspath(path))
            for run in self.obj['import']:
                self.obj['__imported'][run] = HclReader(runfile_dir + '/' + self.obj['import'][run]).getRuns()

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
            "sequence": {"type": "array"},
            "command": {"type": ["string", "array"]},
            "executable": {"type": "string"},
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
        "additionalProperties": False
    }

    def getSettings(self) -> dict:
        if self.obj.get('settings') is None:
            return {}
        if type(self.obj.get('settings')) == list:
            raise runnerExceptions.SchemaValiationError('test', 'settings block should be only one')
        try:
            validate(self.obj.get('settings'), self.__settings_schema)
        except exceptions.ValidationError as err:
            raise runnerExceptions.SchemaValiationError('test', err.message)
        return self.obj['settings']

    def getRuns(self) -> dict:
        for key, value in self.obj['run'].items():
            if '.' in key:
                raise runnerExceptions.SchemaValiationError(key, '\'.\' in run name is not allowed')
            if '-' in key:
                logging.warn(f"using '-' in run name is not adviced : {key}")
            try:
                validate(value, self.__run_schema)
            except exceptions.ValidationError as err:
                raise runnerExceptions.SchemaValiationError(key, err.message)
        return self.obj['run']

    def getImports(self):
        return self.obj['__imported']
