# exceptions.py
from abc import ABC
from myrunner.common.logger import logger

class BaseMyRunnerException(ABC, Exception):
    """Base class for other exceptions"""

    def __init__(self) -> None:
        self.head = ''
        self.tail = 'Aborting'

    def pretty_output(self):
        output = '┌─ Error:' + self.head + '\n'
        if type(self.message) is str:
            output += '│' + self.message + '\n'
        else:
            for line in self.message:
                output += '│' + line + '\n'
        output += '└─' + f'{self.final}{self.tail}'
        logger.print_error(output)


class FileNotFound(BaseMyRunnerException):
    """Raised when the file is not found"""

    def __init__(self, filename='File'):
        super().__init__()

        self.filename = filename
        self.return_code = 1
        self.final = ''
        self.message = f'runsfile \'{filename}\' not found'


class SchemaValiationErrorPedantic(BaseMyRunnerException):
    """Raised when some parameter is not valid"""

    def __init__(self, field, errors, filename=''):
        super().__init__()

        self.message = []
        self.message.append(f'\'{field}\'')
        self.head = filename
        self.final = ''
        self.return_code = 2
        for error in errors:
            if len(error['loc']) == 1:
                self.message.append(error['loc'][0] + ': ' + error['msg'])
            else:
                self.message.append(error['msg'])

        self.field = field

class SchemaValiationError(BaseMyRunnerException):
    """Raised when some parameter is not valid"""

    def __init__(self, parameter, message="Resource not found"):
        super().__init__()

        self.parameter = parameter
        self.message = f"{parameter}: {message}"
        self.final = ''
        self.return_code = 2


class OperationFailedError(BaseMyRunnerException):
    """Raised when an operation fails"""

    def __init__(self, operation, reason="Operation failed"):
        super().__init__(self.message)

        self.operation = operation
        self.reason = reason
        self.message = f"{operation}: {reason}"


class ExecutionAbort(BaseMyRunnerException):
    """Raised when an operation fails"""

    def __init__(self, execution, return_code: int):
        super().__init__()
        self.execution = execution
        self.return_code = int(return_code)
        self.final = ''
        self.message = f"Execution failed! [{return_code}]"

class PyHclError(BaseMyRunnerException):
    """Convert exception from pygohcl"""

    def __init__(self, args):
        super().__init__()
        args = args[13:]
        self.message = ['invalid HCL:']
        self.message.extend(args.split('., '))
        self.head = 'test'
        self.final = ''
        self.return_code = 2


class DockerError(BaseMyRunnerException):
    """ Some error in docker"""

    def __init__(self, message):
        super().__init__()
        self.head = 'Docker interaction'
        self.message = ['Can\'t connect to Docker daemon']
        self.message.append(message)
        self.final = ''
        self.return_code = 3
