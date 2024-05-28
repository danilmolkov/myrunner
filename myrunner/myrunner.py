"""
The executable of MyRunner application
"""
import logging
from . import argParser
from . import hclReader
from . import executionEngine
import myrunner.common.runnerExceptions as runnerExceptions
from jsonschema import exceptions


DEFAULT_RUNLIST = 'runlist.hcl'

def readRuns(file: str) -> dict:
    return hclReader.readRuns(file)


def printrunsTable(file: str):
    runs = readRuns(file)

    padding = len(max(runs, key=len)) + 5
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
        logging.error(f'run {run} is not found')
        return -1
    return executionEngine.execute(runs[run]['execute'])


def main():
    args = argParser.parse()
    logging.info("Starting")
    if args.describe:
        printrunsTable(args.file)
        logging.info('Finished')
        return 0
    runs = readRuns(args.file)
    for run in args.runs:
        rc = executeRun(runs, run)
        if rc != 0:
            exit(rc)
    logging.info('Finished')
    return 0


def loggingSetup():
    logging.getLogger('myrunner')
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')


if __name__ == '__main__':
    try:
        loggingSetup()
        main()
    except runnerExceptions.BaseMyRunnerException as err:
        logging.critical(err)
    #     print(f'EXCEPTION: {err}')
    #     sys.exit(1)
