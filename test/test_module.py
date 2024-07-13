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
        self.runs = self.hcl.getRuns()
        self.setting = self.hcl.getSettings()
        self.imports = self.hcl.getImports()

    def command(self, runToRun: str) -> int:
        return mr.commandRun(self.runs, runToRun, self.imports)


class myRunnerInterface():
    def _command(self, runner, run):
        self.assertEqual(runner.command(run), 0, 'return code is not successfull')

    def _command_failed(self, runner, run):
        self.assertNotEqual(runner.command(run), 0, 'return code is successfull')

    def _clearBuffer(self):
        ExecutionEngine.outputFd.truncate(0)
        ExecutionEngine.outputFd.seek(0)

    def _getResult(self):
        return ExecutionEngine.outputFd.getvalue().rstrip('\n')

class executionTesting(unittest.TestCase, myRunnerInterface):

    def setUp(self) -> None:
        ExecutionEngine.outputFd = StringIO('')
        mr.loggingSetup()

    def tearDown(self):
        ExecutionEngine.outputFd.close()

    def testFirstRun(self):
        firstRunner = testMyRunner('test-runner.hcl')
        self._command(firstRunner, 'first_run')
        result = self._getResult()
        self.assertEqual(
            "Hello World!", result)

    def testMultilineString(self):
        firstRunner = testMyRunner('test-runner.hcl')
        self._command(firstRunner, 'second_run')
        fileContent = ''
        with open('./test/misc/testFile.txt', 'r') as f:
            fileContent = f.read()
        self.assertEqual(fileContent.rstrip('\n'), self._getResult())

    def testScriptInHeridoc(self):
        runner = testMyRunner('test-runner.hcl')
        self._command(runner, 'heredoc_run')
        self.assertEqual(self._getResult(), f'{os.path.basename(os.getcwd())}\nworld!\n12345')

    def testEnvironmentHandling(self):
        runner = testMyRunner('environment-vars.hcl')
        os.environ['TEST_1'] = 'Hello'  # test that this override default
        os.environ['TEST_3'] = 'I won\'t be printed to pass'  # test that not stated won't be provided
        self._command(runner, 'print_env_vars')
        self.assertEqual(self._getResult(), 'Hello world!')
        self._clearBuffer()
        equal_string = 'I will be printed to pass'  # test that will be provided if envs not stated
        os.environ['TESTING_ENV'] = equal_string
        self._command(runner, 'print_envs_if_not_stated')
        self.assertEqual(self._getResult(), equal_string)
        self._clearBuffer()
        self._command(runner, 'print_no_any_envs_except_system')
        self.assertEqual(self._getResult(), '')

    def testExecutableFeature(self):
        runner = testMyRunner('test-runner.hcl')
        self._command(runner, 'python_run')
        self.assertEqual(self._getResult(), 'Combinations: [(1, 2), (1, 3), (2, 3)]\n'
                                            'Original array for sorting: [1, 2, 1, 3, 2, 3]\n'
                                            'Sorted array: [1, 1, 2, 2, 3, 3]')
        self._clearBuffer()

    def testCommandAsArray(self):
        runner = testMyRunner('test-runner.hcl')
        self._command(runner, 'command_array_type')
        equal_string = 'Hi, my name is Billy\nHi, and my name is Garry'
        self.assertEqual(self._getResult(), equal_string)

    def testCommandAsArrayFailure(self):
        runner = testMyRunner('test-runner.hcl')
        self._command_failed(runner, 'command_array_type_failure')
        equal_string = 'I\'m failing'
        self.assertEqual(self._getResult(), equal_string)


class fileReadingTesting(unittest.TestCase):
    def __getRuns(self, path=''):
        HclReader(path).getRuns()

    def __getImports(self, path=''):
        HclReader(path).getImports()

    def testRunListNotFound(self):
        self.assertRaises(runnerExceptions.FileNotFound,
                          self.__getRuns)

    def testInvalidRunnerReading(self):
        self.assertRaises(runnerExceptions.SchemaValiationError, self.__getRuns, path='./test/runners/invalid-rule-runner.hcl')

    def testSuccessImportReading(self):
        try:
            self.__getImports('./test/runners/imports.hcl')
        except Exception:
            self.fail("__getImports raised is failed ")

    def testUnsuccessfulImportReading(self):
        self.assertRaises(runnerExceptions.FileNotFound, self.__getRuns,
                          path='./test/runners/invalid-import.hcl')

class sequenceTesting(unittest.TestCase, myRunnerInterface):
    def setUp(self) -> None:
        ExecutionEngine.outputFd = StringIO('')
        mr.loggingSetup()

    def tearDown(self):
        ExecutionEngine.outputFd.close()

    def testSequence(self):
        runner = testMyRunner('sequence.hcl')
        self._command(runner, 'sequence_successful')
        equal_string = 'Success!\nSuccess!'
        self.assertEqual(self._getResult(), equal_string)

    def testFaliedSequence(self):
        runner = testMyRunner('sequence.hcl')
        self._command_failed(runner, 'sequence_unsuccessful')
        equal_string = 'Success!\nFailing :('
        self.assertEqual(self._getResult(), equal_string)

    def testSequenceOfSequences(self):
        runner = testMyRunner('sequence.hcl')
        self._command_failed(runner, 'run_sequence_of_sequence')
        equal_string = 'Success!\nSuccess!\nSuccess!\nFailing :('
        self.assertEqual(self._getResult(), equal_string)

    def testRunNotFound(self):
        runner = testMyRunner('sequence.hcl')
        equal_string = 'Success!\nSuccess!'
        self.assertRaises(runnerExceptions.SchemaValiationError,
                          self._command_failed, runner=runner,
                          run='run_sequence_with_invalid_run')
        self.assertEqual(self._getResult(), equal_string)


if __name__ == '__main__':
    unittest.main()
