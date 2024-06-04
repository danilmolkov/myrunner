"""
The executable of MyRunner application
"""
import logging
from . import argParser
from .hclReader import HclReader
from . import executionEngine
import myrunner.common.runnerExceptions as runnerExceptions

DEFAULT_RUNLIST = 'runlist.hcl'


def printRunsTable(runs: dict, arg_runs: list):
    padding = len(max(runs, key=len)) + 4
    format_string = "{:<" + str(padding) + "} {:<" + str(padding) + "}"
    print(format_string.format('Name', 'Description'))
    if type(arg_runs) is list:
        for run in arg_runs:
            if run in runs.keys():
                print(format_string.format(run, runs[run].get('description', '')))
                # else:
                # TODO: add no rule found raise
    else:
        for key, value in runs.items():
            print(format_string.format(key, value.get('description', '')))


def executeRun(runs: dict, run: str):
    """Perform run execution

    Args:
        runs (dict): dict of runs
        run (str): run name to run

    Returns:
        int: -1 if run not found
             0 if run is found
    """
    if run not in runs.keys():
        logging.error(f'run \'{run}\' is not found')
        return -1
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
    if args.version:
        try:
            from ._version import version as ver
        except ModuleNotFoundError:
            ver = 'Developing'
            pass
        print(f'Myrunner version {ver}')
        return 0
    hclReader = HclReader(args.file)
    runs = hclReader.getRuns()
    if args.describe:
        printRunsTable(runs, args.runs)
        logging.info('Exiting')
        return 0
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
    main()
