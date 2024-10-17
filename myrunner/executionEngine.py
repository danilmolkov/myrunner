import subprocess
import os
import time
import logging
import signal
import sys
from queue import Empty, Queue
from threading import Thread
import docker

import docker.errors
import myrunner.common.runnerExceptions as runnerExceptions
from .execution_logger import ExecutionLogger

test_signal = None

# TODO: Move everyting under class
class ExecutionEngine:
    el = ExecutionLogger('disable')
    interactiveInput = False

    signal = None

    class DockerInteraction:
        def __init__(self):
            try:
                self.client = docker.from_env()
            except docker.errors.DockerException as e:
                raise runnerExceptions.DockerError(e.args[0])

            self.api = docker.APIClient()

        def __del__(self):
            self.api.close()
            self.client.close()

        def run_container(self, image: str, command: str):
            print(self.client.containers.run(image=image, command=command).decode())

        def run(self, image: str, command: str):
            self.client.images.pull(image)
            try:
                self.__current_container = self.client.containers.run(image,
                                                                      command,
                                                                      detach=True,
                                                                      stdout=True,
                                                                      stderr=True,
                                                                      remove=False)
            except docker.errors.DockerException as e:
                raise runnerExceptions.DockerError(str(e))

        def kill(self, signal: int):
            print('killing with signal', signal)
            self.__current_container.kill(signal)

        def stream_logs(self):
            # Create pipes for stdout and stderr
            stdout_read_pipe, stdout_write_pipe = os.pipe()
            stderr_read_pipe, stderr_write_pipe = os.pipe()
            # Start streaming stdout logs to one pipe and stderr logs to another
            stdout_thread = Thread(target=self.stream_stdout, args=(stdout_write_pipe,))
            stderr_thread = Thread(target=self.stream_stderr, args=(stderr_write_pipe,))

            stdout_thread.start()
            stderr_thread.start()
            output_queue = Queue()
            stdout_reader_thread = Thread(target=self.read_pipe, args=(stdout_read_pipe, output_queue,))
            stderr_reader_thread = Thread(target=self.read_pipe_err, args=(stderr_read_pipe, output_queue,))

            stdout_reader_thread.start()
            stderr_reader_thread.start()

            # When you're done, stop the container and join the threads
            self.__returned = self.__current_container.wait()

            self.collect_logs(output_queue, stdout_reader_thread, stderr_reader_thread)

            stdout_thread.join()
            stderr_thread.join()
            self.__current_container.remove()
            return self.__returned['StatusCode']

        def stream_stdout(self, write_fd):
            container = self.__current_container
            stdout_stream = container.logs(stdout=True, stderr=False, stream=True)
            with os.fdopen(write_fd, 'w') as pipe:
                for log in stdout_stream:
                    pipe.write(log.decode('utf-8'))

        # Function to stream stderr logs
        def stream_stderr(self, write_fd):
            container = self.__current_container
            stderr_stream = container.logs(stdout=False, stderr=True, stream=True)
            with os.fdopen(write_fd, 'w') as pipe:
                for log in stderr_stream:
                    pipe.write(log.decode('utf-8'))

        # Now, you can read from the stdout and stderr pipes in the main process
        def read_pipe(self, pipe_fd, output_queue: Queue):
            with os.fdopen(pipe_fd) as log_pipe:
                while self.__returned is None:
                    log_line = log_pipe.readline()
                    if log_line:
                        output_queue.put(log_line)  # Process or print the log line

        # Now, you can read from the stdout and stderr pipes in the main process
        def read_pipe_err(self, pipe_fd, output_queue: Queue):
            def append_before_last(original_string, to_append):
                return original_string[:-1] + to_append + original_string[-1]
            with os.fdopen(pipe_fd) as log_pipe:
                while self.__returned is None:
                    log_line = log_pipe.readline()
                    if log_line:
                        output_queue.put("\033[91m" + append_before_last(log_line, "\033[0m"))

        def collect_logs(self, output_queue, collector, collector_err) -> None:
            # global test_signal
            output = []
            while True:
                if self.__returned is None:
                    if test_signal != 0:
                        print('calling')
                        self.kill(ExecutionEngine.signal)
                        ExecutionEngine.signal = None
                    try:
                        output.append(output_queue.get(timeout=0.001))
                    except Empty:
                        continue
                    log_subprocess(output[-1])
                else:
                    collector.join()
                    collector_err.join()
                    while True:
                        try:
                            output.append(output_queue.get(timeout=0.001))
                        except Empty:
                            break
                        log_subprocess(output[-1])
                    break

        __current_container = None
        __returned = None

    @staticmethod
    def collect(proc, output: Queue):
        for line in iter(proc.readline, ''):
            output.put(line)

    @staticmethod
    def collect_err(proc, output: Queue):
        def append_before_last(original_string, to_append):
            return original_string[:-1] + to_append + original_string[-1]
        for line in iter(proc.readline, ''):
            output.put("\033[91m" + append_before_last(line, "\033[0m"))

    @staticmethod
    def provideEnvs(envs):
        if envs is None:
            return os.environ
        result = {}
        # add PATH by default
        result['PATH'] = os.environ.get('PATH')
        for env in envs:
            if env_value := os.environ.get(env['name']):
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
    ExecutionEngine.el.set_output_fd(open(os.devnull, 'w', encoding='utf-8'))

def set_logging(mode: str):
    ExecutionEngine.el.set(mode)

def signal_handler(sig, _):
    global test_signal
    logging.warning("Signal received: %d (%s)", sig, signal.Signals(sig).name)
    ExecutionEngine.signal = sig
    test_signal = sig

def collect_logs_from_subprocess(proc, output_queue, collector, collector_err) -> None:
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
            collector_err.join()
            while True:
                try:
                    output.append(output_queue.get(timeout=0.001))
                except Empty:
                    break
                log_subprocess(output[-1])
            break

def log_subprocess(log: str):
    # import textwrap
    for line in log.splitlines(keepends=False):
        ExecutionEngine.el.print_output(line)

def command(run_name: str, command_string: str, envs, executable: str, cwd: str | None, ignore_rc: bool, docker_params={}) -> int:
    """Run simple task
    """
    el = ExecutionEngine.el
    el.print_cwd('/bin/bash' if executable == '' else executable)
    el.print_command(command_string)
    if ExecutionEngine.interactiveInput and ExecutionEngine.askForCommandInput(command_string):
        return 1

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    el.print_runname(run_name)
    rc = None
    start = time.time()
    if docker_params != {}:
        logging.debug('Starting docker')
        docker = ExecutionEngine.DockerInteraction()

        docker.run(image=docker_params['image'], command=command_string)
        rc = docker.stream_logs()
    else:
        with subprocess.Popen(args=command_string,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              shell=True, universal_newlines=True,
                              executable='/bin/bash' if executable == '' else executable,
                              cwd=cwd, pass_fds=(),
                              env=ExecutionEngine.provideEnvs(envs)) as proc:
            output_queue = Queue()
            collector = Thread(target=ExecutionEngine.collect,
                               args=(proc.stdout, output_queue),
                               name='collector', daemon=True)
            collector_err = Thread(target=ExecutionEngine.collect_err,
                                   args=(proc.stderr, output_queue),
                                   name='collector-err', daemon=True)
            start = time.time()
            collector.start()
            collector_err.start()
            collect_logs_from_subprocess(proc, output_queue, collector, collector_err)
            rc = proc.returncode
    end_time = time.time()

    if rc != 0:
        if ignore_rc:
            logging.debug('Completed with non-zero return code. [%d]', rc)
            return 0
        el.print_time(f'Failed, {int(end_time - start)} seconds')
        sys.stdout.flush()
        return rc
    el.print_time(f'Finished, {int(end_time - start)} seconds')
    sys.stdout.flush()
    logging.debug('Command finished')
    return rc
