# exceptions.py
from abc import ABC
class BaseMyRunnerException(ABC, Exception):
    """Base class for other exceptions"""

    def __init__(self) -> None:
        self.head = ''
        self.tail = ''

    def pretty_output(self):
        print('\033[91m┌─ Error', self.head)
        if type(self.message) is str:
            print('│', self.message)
        else:
            for line in self.message:
                print('│', line)
        print('└─', self.final, '\033[0m', self.tail)


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

        self.parameter = parameter
        self.message = f"{parameter}: {message}"
        self.final = ''
        super().__init__()


class OperationFailedError(BaseMyRunnerException):
    """Raised when an operation fails"""

    def __init__(self, operation, reason="Operation failed"):
        self.operation = operation
        self.reason = reason
        self.message = f"{operation}: {reason}"
        super().__init__(self.message)


class ExecutionAbort(BaseMyRunnerException):
    """Raised when an operation fails"""

    def __init__(self, execution, return_code: int):
        self.execution = execution
        self.return_code = return_code
        self.final = ''
        self.message = f"Execution failed! [{return_code}]"
        super().__init__(self.message)
