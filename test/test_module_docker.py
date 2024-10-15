import unittest
import os
from io import StringIO
import myrunner.myrunner as mr
from myrunner.executionEngine import ExecutionEngine
from myrunner.hclReader import HclReader
import myrunner.common.runnerExceptions as runnerExceptions
from .test_common import TestMyRunner

class MyrunnerTestCase(unittest.TestCase):
    def _command(self, runner, run):
        self.assertEqual(runner.command(run), 0, 'return code is not successfull')

    def _command_failed(self, runner, run):
        self.assertNotEqual(runner.command(run), 0, 'return code is successfull')

    def _clearBuffer(self):
        ExecutionEngine.el.get_fd().truncate(0)
        ExecutionEngine.el.get_fd().seek(0)

    def _getResult(self):
        return ExecutionEngine.el.get_fd().getvalue().rstrip('\n')


class DockerExecutionTesting(MyrunnerTestCase):
    def setUp(self) -> None:
        ExecutionEngine.el.set_output_fd(StringIO(''))
        mr.loggingSetup()

    def tearDown(self):
        ExecutionEngine.el.get_fd().close()

    def testFirstRun(self):
        run = """
run "first-docker-test" {
    docker {
        image = "alpine"
    }
    command = "echo 'Hello from docker!'"
    ignore_retcode = true
}
        """.encode("utf-8")
        runner = TestMyRunner(None, data=run)
        self._command(runner, 'first-docker-test')
        result = self._getResult()
        self.assertEqual(
            "Hello from docker!", result)

if __name__ == '__main__':
    unittest.main()