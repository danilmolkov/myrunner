import unittest
import os
from io import StringIO
import myrunner.myrunner as mr
from myrunner.executionEngine import ExecutionEngine
from myrunner.hclReader import HclReader
import myrunner.common.runnerExceptions as runnerExceptions

class TestMyRunner:
    def __init__(self, runlist_name: str | None, data=None) -> None:
        if data is not None and runlist_name is None:
            self.hcl = HclReader(data)
        else:
            self.runners_path = f'{os.path.dirname(__file__)}/runners'
            self.hcl = HclReader(f'{self.runners_path}/{runlist_name}')
        self.runs = self.hcl.getruns()
        self.setting = self.hcl.getsettings()
        self.imports = self.hcl.getimports()

    def command(self, runToRun: str) -> int:
        return mr.commandRun(self.runs, runToRun, self.imports)


class MyrunnerTestCase(unittest.TestCase):
    def _command(self, runner, run):
        self.assertEqual(runner.command(run), 0, 'return code is not successfull')

    def _command_failed(self, runner, run):
        self.assertNotEqual(runner.command(run), 0, 'return code is successfull')

    def _clearBuffer(self):
        ExecutionEngine.outputFd.truncate(0)
        ExecutionEngine.outputFd.seek(0)

    def _getResult(self):
        return ExecutionEngine.outputFd.getvalue().rstrip('\n')

class ExecutionTesting(MyrunnerTestCase):

    def setUp(self) -> None:
        ExecutionEngine.outputFd = StringIO('')
        mr.loggingSetup()

    def tearDown(self):
        ExecutionEngine.outputFd.close()

    def testFirstRun(self):
        firstRunner = TestMyRunner('test-runner.hcl')
        self._command(firstRunner, 'first_run')
        result = self._getResult()
        self.assertEqual(
            "Hello World!", result)

    def testMultilineString(self):
        firstRunner = TestMyRunner('test-runner.hcl')
        self._command(firstRunner, 'second_run')
        fileContent = ''
        with open('./test/misc/testFile.txt', 'r') as f:
            fileContent = f.read()
        self.assertEqual(fileContent.rstrip('\n'), self._getResult())

    def testScriptInHeridoc(self):
        runner = TestMyRunner('test-runner.hcl')
        self._command(runner, 'heredoc_run')
        self.assertEqual(self._getResult(), f'{os.path.basename(os.getcwd())}\nworld!\n12345')

    def testEnvironmentHandling(self):
        runner = TestMyRunner('environment-vars.hcl')
        # test that this override default
        os.environ['TEST_1'] = 'Hello'
        # test that not stated won't be provided
        os.environ['TEST_3'] = 'I won\'t be printed to pass'
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
        runner = TestMyRunner('test-runner.hcl')
        self._command(runner, 'python_run')
        self.assertEqual(self._getResult(), 'Combinations: [(1, 2), (1, 3), (2, 3)]\n'
                                            'Original array for sorting: [1, 2, 1, 3, 2, 3]\n'
                                            'Sorted array: [1, 1, 2, 2, 3, 3]')
        self._clearBuffer()

    def testCommandAsArray(self):
        runner = TestMyRunner('test-runner.hcl')
        self._command(runner, 'command_array_type')
        equal_string = 'Hi, my name is Billy\nHi, and my name is Garry'
        self.assertEqual(self._getResult(), equal_string)

    def testCommandAsArrayFailure(self):
        runner = TestMyRunner('test-runner.hcl')
        self._command_failed(runner, 'command_array_type_failure')
        equal_string = 'I\'m failing'
        self.assertEqual(self._getResult(), equal_string)


class FileReadingTesting(unittest.TestCase):
    def __getruns(self, path=''):
        HclReader(path).getruns()

    def __getimports(self, path=''):
        HclReader(path).getimports()

    def testRunListNotFound(self):
        self.assertRaises(runnerExceptions.FileNotFound,
                          self.__getruns)

    def testInvalidRunnerReading(self):
        self.assertRaises(runnerExceptions.SchemaValiationError, self.__getruns, path='./test/runners/invalid-rule-runner.hcl')

    def testSuccessImportReading(self):
        try:
            self.__getimports('./test/runners/imports.hcl')
        except Exception:
            self.fail("__getimports raised is failed ")

    def testUnsuccessfulImportReading(self):
        self.assertRaises(runnerExceptions.FileNotFound, self.__getruns,
                          path='./test/runners/invalid-import.hcl')

class SequenceTesting(MyrunnerTestCase):
    def setUp(self) -> None:
        ExecutionEngine.outputFd = StringIO('')
        mr.loggingSetup()

    def tearDown(self):
        ExecutionEngine.outputFd.close()

    def testSequence(self):
        runner = TestMyRunner('sequence.hcl')
        self._command(runner, 'sequence_successful')
        equal_string = 'Success!\nSuccess!'
        self.assertEqual(self._getResult(), equal_string)

    def testFaliedSequence(self):
        runner = TestMyRunner('sequence.hcl')
        self._command_failed(runner, 'sequence_unsuccessful')
        equal_string = 'Success!\nFailing :('
        self.assertEqual(self._getResult(), equal_string)

    def testSequenceOfSequences(self):
        runner = TestMyRunner('sequence.hcl')
        self._command_failed(runner, 'run_sequence_of_sequence')
        equal_string = 'Success!\nSuccess!\nSuccess!\nFailing :('
        self.assertEqual(self._getResult(), equal_string)

    def testRunNotFound(self):
        runner = TestMyRunner('sequence.hcl')
        equal_string = 'Success!\nSuccess!'
        self.assertRaises(runnerExceptions.SchemaValiationError,
                          self._command_failed, runner=runner,
                          run='run_sequence_with_invalid_run')
        self.assertEqual(self._getResult(), equal_string)

class IgnoreRetCodeTesting(MyrunnerTestCase):
    def setUp(self) -> None:
        ExecutionEngine.outputFd = StringIO('')
        mr.loggingSetup()

    def testRunExecution(self):
        data = """
run "test_rc" {
    description = ""
    command = "gergebqerbqg"
    ignore_retcode = true
}
        """.encode("utf-8")

        runner = TestMyRunner(None, data=data)
        self._command(runner, 'test_rc')

    def testRunSequence(self):
        data = """
run "test_rc" {
    command = "function fail_function() { echo 'Failing :('; return 1; }; fail_function"
    ignore_retcode = true
}
run "seq_rc" {
    sequence = [
        # should pass
        test_rc
    ]
    # should not pass as no ignore_retcode
    command = "function fail_function() { echo 'Failing :('; return 1; }; fail_function"
}
        """.encode("utf-8")

        runner = TestMyRunner(None, data=data)
        self._command_failed(runner, 'seq_rc')
        self.assertEqual(self._getResult(), 'Failing :(\nFailing :(')


if __name__ == '__main__':
    unittest.main()
