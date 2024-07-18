import subprocess
import os
import logging
import sys
import signal
from queue import Empty, Queue
from threading import Thread

# TODO: Move everyting under class
class ExecutionEngine:
    outputFd = sys.stdout
    interactiveInput = False

    signal = None

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
    def askForCommandInput(cmd: str):
        if input(f'Running {cmd}. Type \'yes\' to run: ') in ['yes', '\'yes\'', '"yes"']:
            return 0
        return 1

def disableOutput():
    ExecutionEngine.outputFd = open(os.devnull, 'w', encoding='utf-8')

def signal_handler(sig, _):
    logging.warning("Signal received: %d (%s)", sig, signal.Signals(sig).name)
    ExecutionEngine.signal = sig

def collect_logs_from_subprocess(proc, output_queue, collector) -> None:
    output = []
    while True:
        if proc.poll() is None:
            if ExecutionEngine.signal:
                proc.send_signal(ExecutionEngine.signal)
                ExecutionEngine.signal = None
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

def command(command_string: str, envs, executable: str, cwd: str | None, ignore_rc: bool) -> int:
    """Run simple task
    """
    newline = ' '
    if '\n' in command_string:
        newline = '\n'
    logging.info('Executing command:%s%s', newline, command_string)
    if ExecutionEngine.interactiveInput and ExecutionEngine.askForCommandInput(command_string):
        return 1

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    with subprocess.Popen(args=command_string,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          shell=True, universal_newlines=True,
                          executable='/bin/bash' if executable == '' else executable,
                          cwd=cwd, pass_fds=(),
                          env=ExecutionEngine.provideEnvs(envs)) as proc:
        output_queue = Queue()
        collector = Thread(target=ExecutionEngine.collect,
                           args=(proc.stdout, output_queue),
                           name='collector', daemon=True)
        collector.start()
        collect_logs_from_subprocess(proc, output_queue, collector)
        if (rc := proc.returncode) != 0:
            if ignore_rc:
                logging.info('Completed with non-zero return code. [%d]', rc)
                return 0
            logging.error('Command failed! [%d]', rc)
            return rc

        logging.info('Command finished')
        return rc
