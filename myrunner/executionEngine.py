import subprocess
import os
import logging
import sys


class ExecutionEngine:
    outputFd = sys.stdout


def execute(command) -> int:
    """Run simple task
    """
    logging.info(f'Executing command: {command}')
    print()
    with subprocess.Popen(args=command,
                          stdout=subprocess.PIPE, shell=True, stderr=subprocess.STDOUT, universal_newlines=True, executable='/bin/sh', cwd=os.getcwd(), pass_fds=()) as proc:
        # while proc.poll() is None:
        #   continue
        output = []
        while proc.poll() is None:
            for line in iter(proc.stdout.read, ''):
                output.append(line)
        for line in output:
            print(line, end='', file=ExecutionEngine.outputFd)
        print('', file=ExecutionEngine.outputFd)
        rc = proc.returncode
        if rc != 0:
            logging.error('Command failed!')
        logging.info('Command finished')
        return rc
