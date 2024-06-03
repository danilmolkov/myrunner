# exceptions.py

class BaseMyRunnerException(Exception):
    """Base class for other exceptions"""
    pass


class FileNotFound(BaseMyRunnerException):
    """Raised when the file is not found"""

    def __init__(self, filename='File'):
        self.filename = filename
        self.message = f'runsfile \'{filename}\' not found.'
        super().__init__(self.message)


class SchemaValiationError(BaseMyRunnerException):
    """Raised when a resource is not found"""

    def __init__(self, resource, message="Resource not found"):
        self.resource = resource
        self.message = f"{resource}: {message}"
        super().__init__(self.message)


class OperationFailedError(BaseMyRunnerException):
    """Raised when an operation fails"""

    def __init__(self, operation, reason="Operation failed"):
        self.operation = operation
        self.reason = reason
        self.message = f"{operation}: {reason}"
        super().__init__(self.message)
