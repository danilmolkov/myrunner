"""
The executable of MyRunner application
"""
import logging
from posixpath import basename

from . import argParser
from .hclReader import HclReader
from . import executionEngine
import myrunner.common.runnerExceptions as runnerExceptions

from sys import argv

def printRunListDescribe(file: str, desc: str):
    output = basename(file)
    if desc:
        output = output + ': ' + desc + '\n'
    print(output)

def printRunsTable(runs: dict, arg_runs: list):
    padding = len(max(runs, key=len)) + 4
    format_string = "{:<" + str(padding) + "} {:<" + str(padding) + "}"
    for run in arg_runs:
        if run not in runs:
            raise runnerExceptions.SchemaValiationError(run, 'run is not found')
    print(format_string.format('Name', 'Description'))
    if len(arg_runs) != 0:
        for run in arg_runs:
            if run in runs.keys():
                print(format_string.format(run, runs[run].get('description', '')))
    else:
        for key, value in runs.items():
            print(format_string.format(key, value.get('description', '')))


def commandRun(runs: dict, run: str):
    """Perform run execution

    Args:
        runs (dict): dict of runs
        run (str): run name to run

    Returns:
        int: -1 if run not found
             0 if run is found
    Raises:
        runnerExceptions.SchemaValiationError if run is not found
    """
    if run not in runs:
        raise runnerExceptions.SchemaValiationError('test', f'run {run} not found')
    if type(runs[run]['command']) is str:
        return executionEngine.command(runs[run]['command'], runs[run].get('envs', None), runs[run].get('executable', ''))
    else:
        rc = 0
        for command in runs[run]['command']:
            rc = executionEngine.command(command, runs[run].get('envs', None), runs[run].get('executable', ''))
            if rc != 0:
                return rc
        return rc

def getVersion():
    try:
        from ._version import version as ver
    except ModuleNotFoundError:
        ver = 'Developing'
        pass
    print(f'Myrunner version {ver}')

def isComplete():
    if argv[1] == '--complete':
        try:
            runs = HclReader(argv[2]).readRuns().keys()
            print(" ".join(list(runs)))
        except runnerExceptions.FileNotFound:
            pass
        exit(0)

def printCompletionScript():
    from os import path as ph
    script_dir = ph.dirname(ph.abspath(__file__))
    with open(f'{script_dir}/autocomplete/autocomplete.sh', 'r') as f:
        print(f.read())

def main():
    isComplete()
    try:
        start()
    except runnerExceptions.BaseMyRunnerException as err:
        logging.error(err)
        exit(1)

def start():
    loggingSetup()
    args = argParser.parse()
    if args.completion:
        printCompletionScript()
    hclReader = HclReader(args.file)
    if args.version:
        getVersion()
        return 0
    runs_file_settings = hclReader.readSettings()
    if args.quite or args.quite_all:
        logging.disable(logging.CRITICAL)
    if args.quite_all:
        executionEngine.disableOutput()
    runs = hclReader.readRuns()
    settings = hclReader.readSettings()
    if args.describe:
        printRunListDescribe(args.file, settings.get('description', ''))
        printRunsTable(runs, args.runs)
        logging.info('Exiting')
        return 0
    if args.interactive or runs_file_settings.get('interactive', False):
        executionEngine.ExecutionEngine.interactiveInput = True
        logging.debug('interactive')
    for run in args.runs:
        logging.info(f"Starting run: {run}")
        rc = commandRun(runs, run)
        if rc != 0:
            logging.error('Execution failed')
            exit(rc)
    return 0

def loggingSetup():
    # note: critical is not used
    logging.getLogger('myrunner')
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')


if __name__ == '__main__':
    main()
