import subprocess
import os
import logging
import sys
from queue import Empty, Queue
from threading import Thread

DELIM = '========================='

# TODO: Move everyting under class
class ExecutionEngine:
    outputFd = sys.stdout
    interactiveInput = False

    @staticmethod
    def collect(proc, output: Queue):
        for line in iter(proc.readline, ''):
            output.put(line)

    @staticmethod
    def provideEnvs(envs):
        if envs is None:
            return os.environ
        result = {}
        for env in envs:
            env_value = os.environ.get(env['name'])
            if env_value:
                result[env['name']] = env_value
                continue
            result[env['name']] = env['default']
        return result

    @staticmethod
    def askForCommandInput(command: str):
        answer = input(f'Running {command}. Type \'yes\' to run: ')
        if answer in ['yes', '\'yes\'', '"yes"']:
            return 0
        return 1

def disableOutput():
    ExecutionEngine.outputFd = open(os.devnull, 'w')

def collectLogsFromSubprocess(proc, output_queue, collector) -> None:
    output = []
    while True:
        if proc.poll() is None:
            try:
                output.append(output_queue.get(timeout=0.001))
            except Empty:
                continue
            log_subprocess(output[-1])
        else:
            # proc finished
            collector.join()
            while True:
                try:
                    output.append(output_queue.get(timeout=0.001))
                except Empty:
                    break
                log_subprocess(output[-1])
            break

def log_subprocess(log: str):
    for line in log.splitlines():
        print(line, file=ExecutionEngine.outputFd)

def command(command: str, envs, executable: str) -> int:
    """Run simple task
    """
    newline = ' '
    if '\n' in command:
        newline = '\n'
    logging.info(f'Executing command:{newline}{command}')
    if ExecutionEngine.interactiveInput and ExecutionEngine.askForCommandInput(command):
        return 1

    with subprocess.Popen(args=command,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          shell=True, universal_newlines=True,
                          executable='/bin/bash' if executable == '' else executable,
                          cwd=os.getcwd(), pass_fds=(),
                          env=ExecutionEngine.provideEnvs(envs)) as proc:
        output_queue = Queue()
        collector = Thread(target=ExecutionEngine.collect,
                           args=(proc.stdout, output_queue),
                           name='collector', daemon=True)
        collector.start()
        collectLogsFromSubprocess(proc, output_queue, collector)
        rc = proc.returncode
        if rc != 0:
            logging.error(f'Command failed! [{rc}]')
        logging.info('Command finished')
        return rc
