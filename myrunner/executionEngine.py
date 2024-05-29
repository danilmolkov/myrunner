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

    @staticmethod
    def collect(proc, output: Queue):
        for line in iter(proc.readline, ''):
            output.put(line)

def log_subprocess(log: str):
    for line in log.splitlines():
        print(line, file=ExecutionEngine.outputFd)

def execute(command) -> int:
    """Run simple task
    """
    logging.info(f'Executing command: {command}')
    print(DELIM)
    with subprocess.Popen(args=command,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          shell=True, universal_newlines=True,
                          executable='/bin/sh', cwd=os.getcwd(), pass_fds=()) as proc:
        output_queue = Queue()
        collector = Thread(target=ExecutionEngine.collect, args=(proc.stdout, output_queue), name='collector', daemon=True)
        collector.start()
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
        print(DELIM)
        rc = proc.returncode
        if rc != 0:
            logging.error('Command failed!')
        logging.info('Command finished')
        return rc
