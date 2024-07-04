import myrunner.myrunner as mr
from myrunner.executionEngine import ExecutionEngine
from myrunner.hclReader import HclReader
import myrunner.common.runnerExceptions as runnerExceptions
import unittest
import os
from io import StringIO

class testMyRunner:
    def __init__(self, runnerName: str) -> None:
        self.runners_path = f'{os.path.dirname(__file__)}/runners'
        self.hcl = HclReader(f'{self.runners_path}/{runnerName}')
        self.runs = self.hcl.readRuns()
        self.setting = self.hcl.readSettings()

    def command(self, runToRun: str) -> int:
        return mr.commandRun(self.runs, runToRun)


# class TestModule(unittest.TestCase):
class executionTesting(unittest.TestCase):

    def setUp(self) -> None:
        ExecutionEngine.outputFd = StringIO('')
        mr.loggingSetup()

    def tearDown(self):
        ExecutionEngine.outputFd.close()

    def __command(self, runner, run):
        self.assertEqual(runner.command(run), 0, 'return code is not successfull')

    def __command_failed(self, runner, run):
        self.assertNotEqual(runner.command(run), 0, 'return code is successfull')

    def __clearBuffer(self):
        ExecutionEngine.outputFd.truncate(0)
        ExecutionEngine.outputFd.seek(0)

    def __getResult(self):
        return ExecutionEngine.outputFd.getvalue().rstrip('\n')

    def testFirstRun(self):
        firstRunner = testMyRunner('test-runner.hcl')
        self.__command(firstRunner, 'first_run')
        result = self.__getResult()
        self.assertEqual(
            "Hello World!", result)

    def testMultilineString(self):
        firstRunner = testMyRunner('test-runner.hcl')
        self.__command(firstRunner, 'second_run')
        fileContent = ''
        with open('./test/misc/testFile.txt', 'r') as f:
            fileContent = f.read()
        self.assertEqual(fileContent.rstrip('\n'), self.__getResult())

    def testScriptInHeridoc(self):
        runner = testMyRunner('test-runner.hcl')
        self.__command(runner, 'heredoc_run')
        self.assertEqual(self.__getResult(), 'myrunner\nworld!\n12345')

    def testEnvironmentHandling(self):
        runner = testMyRunner('environment-vars.hcl')
        os.environ['TEST_1'] = 'Hello'  # test that this override default
        os.environ['TEST_3'] = 'I won\'t be printed to pass'  # test that not stated won't be provided
        self.__command(runner, 'print_env_vars')
        self.assertEqual(self.__getResult(), 'Hello world!')
        self.__clearBuffer()
        equal_string = 'I will be printed to pass'  # test that will be provided if envs not stated
        os.environ['TESTING_ENV'] = equal_string
        self.__command(runner, 'print_envs_if_not_stated')
        self.assertEqual(self.__getResult(), equal_string)
        self.__clearBuffer()
        self.__command(runner, 'print_no_any_envs_except_system')
        self.assertEqual(self.__getResult(), '')

    def testExecutableFeature(self):
        runner = testMyRunner('test-runner.hcl')
        self.__command(runner, 'python_run')
        self.assertEqual(self.__getResult(), 'Combinations: [(1, 2), (1, 3), (2, 3)]\n'
                                             'Original array for sorting: [1, 2, 1, 3, 2, 3]\n'
                                             'Sorted array: [1, 1, 2, 2, 3, 3]')
        self.__clearBuffer()

    def testCommandAsArray(self):
        runner = testMyRunner('test-runner.hcl')
        self.__command(runner, 'command_array_type')
        equal_string = 'Hi, my name is Billy\nHi, and my name is Garry'
        self.assertEqual(self.__getResult(), equal_string)

    def testCommandAsArrayFailure(self):
        runner = testMyRunner('test-runner.hcl')
        self.__command_failed(runner, 'command_array_type_failure')
        equal_string = 'I\'m failing'
        self.assertEqual(self.__getResult(), equal_string)


class fileReadingTesting(unittest.TestCase):
    def __readRuns(self, path=''):
        HclReader(path).readRuns()

    def __readSettings(self, path=''):
        HclReader(path).readSettings()

    def testRunListNotFound(self):
        self.assertRaises(runnerExceptions.FileNotFound,
                          self.__readRuns)

    def testInvalidRunnerReading(self):
        self.assertRaises(runnerExceptions.SchemaValiationError, self.__readRuns, path='./test/runners/invalid-rule-runner.hcl')


if __name__ == '__main__':

    unittest.main()
