import pygohcl
import logging
from jsonschema import validate, exceptions
import os.path

import myrunner.common.runnerExceptions as runnerExceptions

class HclReader:
    def __init__(self, path: str) -> None:
        self.__filepath = path
        if not os.path.exists(path) or os.path.isdir(path):
            raise runnerExceptions.FileNotFound(path)
        with open(path, 'r') as file:
            # hcl syntax check
            self.obj = pygohcl.loads(file.read())

        # define paths
        self.__paths = {}
        self.__paths['hcl'] = os.path.dirname(os.path.abspath(path))
        self.__paths['cwd'] = os.getcwd()

        # importing runlists
        self.obj['__imported'] = {}
        if 'import' in self.obj:
            for run in self.obj['import']:
                self.obj['__imported'][run] = HclReader(f"{self.__paths['hcl']}/{self.obj['import'][run]}").getRuns()

    __filepath = ""

    __builtin_consts = {
        "path": {
            "runfile": "",
            "pwd": ""
        }
    }

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
            "cwd": {"type": ["null", "string"]},
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
                raise runnerExceptions.SchemaValiationError(key, f'{self.__filepath}: \'.\' in run name is not allowed')
            if '-' in key:
                logging.warn(f"{self.__filepath}: using '-' in run name is not adviced : {key}")
            try:
                validate(value, self.__run_schema)
            except exceptions.ValidationError as err:
                raise runnerExceptions.SchemaValiationError(key, err.message)
            if value.get('cwd') is not None:
                if value['cwd'] != "":
                    value['cwd'] = self.__paths['hcl'] + '/' + value['cwd']
                else:
                    value['cwd'] = self.__paths['hcl']
            else:
                value['cwd'] = None
        return self.obj['run']

    def getImports(self):
        return self.obj['__imported']
