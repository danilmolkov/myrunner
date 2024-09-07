# exceptions.py
from abc import ABC
class BaseMyRunnerException(ABC, Exception):
    """Base class for other exceptions"""

    def pretty_output(self):
        print('\033[91m┌─ Error')
        if type(self.message) is str:
            print('│', self.message)
        else:
            for line in self.message:
                print('│', line)
        print('└─', '\033[0m')


class FileNotFound(BaseMyRunnerException):
    """Raised when the file is not found"""

    def __init__(self, filename='File'):
        self.filename = filename
        self.message = f'runsfile \'{filename}\' not found.'
        super().__init__(self.message)


class SchemaValiationErrorPedantic(BaseMyRunnerException):
    """Raised when some parameter is not valid"""

    def __init__(self, field, errors):

        self.message = []
        self.message.append(f'{field}')
        for error in errors:
            self.message.append(error['loc'][0] + ': ' + error['msg'])

        self.field = field
        super().__init__(self.message)

class SchemaValiationError(BaseMyRunnerException):
    """Raised when some parameter is not valid"""

    def __init__(self, parameter, message="Resource not found"):

        self.parameter = parameter
        self.message = f"{parameter}: {message}"
        super().__init__(self.message)


class OperationFailedError(BaseMyRunnerException):
    """Raised when an operation fails"""

    def __init__(self, operation, reason="Operation failed"):
        self.operation = operation
        self.reason = reason
        self.message = f"{operation}: {reason}"
        super().__init__(self.message)


class ExecutionAbort(BaseMyRunnerException):
    """Raised when an operation fails"""

    def __init__(self, execution, reason="Execution aborted"):
        self.execution = execution
        self.reason = reason
        self.message = f"{execution} aborted: {reason}"
        super().__init__(self.message)
