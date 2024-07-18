import os.path
import logging

import pygohcl
from jsonschema import validate, exceptions

import myrunner.common.runnerExceptions as runnerExceptions

class HclReader:
    def __init__(self, data: str | bytes) -> None:
        if isinstance(data, bytes):
            self.__filepath = ''
            self.obj = pygohcl.loadb(data)
        else:
            # open file
            self.__filepath = data
            if not os.path.exists(data) or os.path.isdir(data):
                raise runnerExceptions.FileNotFound(data)
            with open(data, 'r', encoding='utf-8') as file:
                # hcl syntax check
                self.obj = pygohcl.loads(file.read())

        # define paths
        self.__paths = {}
        self.__paths['hcl'] = os.path.dirname(os.path.abspath(data))
        self.__paths['cwd'] = os.getcwd()

        # importing runlists
        self.obj['__imported'] = {}
        if 'import' in self.obj:
            for run in self.obj['import']:
                self.obj['__imported'][run] = HclReader(f"{self.__paths['hcl']}/{self.obj['import'][run]}").getruns()

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
            "ignore_retcode": {"type": "boolean"},
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

    def getsettings(self) -> dict:
        """get settings block and its content
        """
        if self.obj.get('settings') is None:
            return {}
        if isinstance(self.obj.get('settings'), list):
            raise runnerExceptions.SchemaValiationError('test', 'settings block should be only one')
        try:
            validate(self.obj.get('settings'), self.__settings_schema)
        except exceptions.ValidationError as err:
            raise runnerExceptions.SchemaValiationError('test', err.message)
        return self.obj['settings']

    def getruns(self) -> dict:
        for key, value in self.obj['run'].items():
            if '.' in key:
                raise runnerExceptions.SchemaValiationError(key,
                                                            f'{self.__filepath}: \'.\' '
                                                            'in run name is not allowed')
            if '-' in key:
                logging.warning('%s: using \'-\' in run name is not adviced : %s',
                                self.__filepath, key)
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

    def getimports(self) -> dict:
        """Return imports from provided runlist

        Returns:
            dict: imported runs
        """
        return self.obj['__imported']
