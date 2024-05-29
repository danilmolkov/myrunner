import myrunner.myrunner as mr
from myrunner.executionEngine import ExecutionEngine
import myrunner.common.runnerExceptions as runnerExceptions
import unittest
import os
from io import StringIO

class testMyRunner:
    def __init__(self, runnerName: str) -> None:
        self.runners_path = f'{os.path.dirname(__file__)}/runners'
        self.runs = mr.readRuns(f'{self.runners_path}/{runnerName}')

    def execute(self, runToRun: str) -> int:
        return mr.executeRun(self.runs, runToRun)


# class TestModule(unittest.TestCase):
class executionTesting(unittest.TestCase):

    def setUp(self) -> None:
        ExecutionEngine.outputFd = StringIO('')
        mr.loggingSetup()

    def testFirstRun(self):
        firstRunner = testMyRunner('first-runner.hcl')
        firstRunner.execute('first_run')
        result = ExecutionEngine.outputFd.getvalue().rstrip('\n')
        self.assertEqual(
            "Hello World!", result)

    def testMultilineString(self):
        firstRunner = testMyRunner('first-runner.hcl')
        firstRunner.execute('second_run')
        result = ExecutionEngine.outputFd.getvalue().rstrip('\n')
        fileContent = ''
        with open('./test/misc/testFile.txt', 'r') as f:
            fileContent = f.read()
        self.assertEqual(fileContent.rstrip('\n'), result)

class fileReadingTesting(unittest.TestCase):
    def __readRuns(self, path=''):
        mr.readRuns(path)

    def testRunListNotFound(self):
        self.assertRaises(runnerExceptions.FileNotFound,
                          self.__readRuns)

    def testInvalidRunnerReading(self):
        self.assertRaises(runnerExceptions.SchemaValiationError, self.__readRuns, path='./test/runners/invalid-rule-runner.hcl')


if __name__ == '__main__':

    unittest.main()
