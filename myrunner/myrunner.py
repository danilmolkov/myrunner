"""
The executable of MyRunner application
"""
import logging

from . import argParser
from .hclReader import HclReader
from . import executionEngine
import myrunner.common.runnerExceptions as runnerExceptions

DEFAULT_RUNLIST = 'runlist.hcl'

def printRunsTable(runs, cmdRuns):
    padding = len(max(runs, key=len)) + 4
    format_string = "{:<" + str(padding) + "} {:<" + str(padding) + "}"
    for run in cmdRuns:
        if run not in runs:
            raise runnerExceptions.SchemaValiationError('test', f'run {run} not found')
    print(format_string.format('Name', 'Description'))
    for key, value in runs.items():
        if key in cmdRuns or len(cmdRuns) == 0:
            print(format_string.format(key, value['description']))


def executeRun(runs: dict, run: str):
    """Perform run execution

    Args:
        runs (dict): dict of runs
        run (str): run name to run

    Returns:
        int: -1 if run not found
             0 if run is found
    """
    if run not in runs:
        raise runnerExceptions.SchemaValiationError('test', f'run {run} not found')
    return executionEngine.execute(runs[run]['execute'], runs[run].get('envs', None))

def main():
    try:
        start()
    except runnerExceptions.BaseMyRunnerException as err:
        logging.error(err)
        exit(1)

def start():
    loggingSetup()
    args = argParser.parse()
    hclReader = HclReader(args.file)
    if args.version:
        try:
            from ._version import version as ver
        except ModuleNotFoundError:
            ver = 'Developing'
            pass
        print(f'Myrunner version {ver}')
        return 0
    runs_file_settings = hclReader.readSettings()
    if args.quite or args.quite_all:
        logging.disable(logging.CRITICAL)
    if args.quite_all:
        executionEngine.disableOutput()
    runs = hclReader.readRuns()
    if args.describe:
        printRunsTable(runs, args.runs)
        # logging.error(f'run \'{run}\' is not found')
        # return -1
        logging.info('Exiting')
        return 0
    if args.interactive or runs_file_settings.get('interactive', False):
        executionEngine.ExecutionEngine.interactiveInput = True
        logging.debug('interactive')
    for run in args.runs:
        logging.info(f"Starting run: {run}")
        rc = executeRun(runs, run)
        if rc != 0:
            logging.error('Execution failed')
            exit(rc)
    logging.info('Exiting')
    return 0


def loggingSetup():
    # note: critical is not used
    logging.getLogger('myrunner')
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')


if __name__ == '__main__':
    main()
