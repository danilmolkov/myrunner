"""
The executable of MyRunner application
"""
import logging
from . import argParser
from .hclReader import HclReader
from . import executionEngine
import myrunner.common.runnerExceptions as runnerExceptions

DEFAULT_RUNLIST = 'runlist.hcl'

# TODO: refactor this
def readRunner(file: str) -> dict:
    hclReader = HclReader(file)
    return hclReader.readRuns()


def printRunsTable(file: str):
    runs = readRunner(file)

    padding = len(max(runs, key=len)) + 4
    format_string = "{:<" + str(padding) + "} {:<" + str(padding) + "}"
    print(format_string.format('Name', 'Description'))
    for key, value in runs.items():
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
        logging.error(f'run \'{run}\' is not found')
        return -1
    return executionEngine.execute(runs[run]['execute'], runs[run].get('envs', None))


def main():
    loggingSetup()
    args = argParser.parse()
    if args.version:
        try:
            from ._version import version as ver
        except ModuleNotFoundError:
            print('Developing')
            return 0
        print(ver)
        return 0
    if args.describe:
        printRunsTable(args.file)
        logging.info('Exiting')
        return 0
    runs = readRunner(args.file)
    for run in args.runs:
        logging.info(f"Starting run: {run}")
        rc = executeRun(runs, run)
        if rc != 0:
            logging.info('Exiting')
            exit(rc)
    logging.info('Exiting')
    return 0


def loggingSetup():
    logging.getLogger('myrunner')
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')


if __name__ == '__main__':
    try:
        main()
    except runnerExceptions.BaseMyRunnerException as err:
        logging.critical(err)
        exit(1)
