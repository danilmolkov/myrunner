"""
The executable of MyRunner application
"""
import logging
from posixpath import basename
from sys import argv
from os import path as ph

from . import arg_parser
from .hclReader import HclReader
from . import executionEngine
import myrunner.common.runnerExceptions as runnerExceptions

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


def handleImported(run: str, imports):
    path = run.split('.', 1)
    # sequence imported is currently not working
    # importing imported is currently not working
    if path[0] not in imports:
        raise runnerExceptions.SchemaValiationError('test', f'import {path[0]} not found')
    return commandRun(imports[path[0]], path[1], None)


def commandRun(runs: dict, run: str, imports):
    """Perform run execution

    Args:
        runs (dict): dict of runs
        run (str): run name to run
        imports (dict): imports of runlist

    Returns:
        int: -1 if run not found
             0 if run is found
    Raises:
        runnerExceptions.SchemaValiationError if run is not found
    """
    if run not in runs:
        raise runnerExceptions.SchemaValiationError(run, 'run is not found')
    logging.debug("Starting run: %s", run)

    if 'sequence' in runs[run]:
        for sequence_run in runs[run]['sequence']:
            rc = 0
            if '.' in sequence_run:
                rc = handleImported(sequence_run, imports)
            else:
                rc = commandRun(runs, sequence_run, imports)
            if rc != 0:
                return rc

    if 'command' not in runs[run]:
        return 0
    if isinstance(runs[run]['command'], str):
        return executionEngine.command(run, runs[run]['command'], runs[run].get('envs', None),
                                       runs[run].get('executable', ''), cwd=runs[run]['cwd'],
                                       ignore_rc=runs[run].get('ignore_retcode', False))
    rc = 0
    current = 1
    for command in runs[run]['command']:
        size = len(runs[run]['command'])
        rc = executionEngine.command(f'{run} ({current}/{size})',
                                     command, runs[run].get('envs', None),
                                     runs[run].get('executable', ''), cwd=runs[run]['cwd'],
                                     ignore_rc=runs[run].get('ignore_retcode', False))
        current = current + 1
        if rc != 0:
            return rc
    return rc

def getversion() -> None:
    """get version of myrunner
    """
    try:
        from ._version import version as ver
    except ModuleNotFoundError:
        ver = 'Developing'
    print(f'Myrunner version {ver}')

def iscomplete():
    if len(argv) > 1 and argv[1] == '--complete':
        try:
            runs = HclReader(argv[2]).getruns().keys()
            print(" ".join(list(runs)))
        except runnerExceptions.FileNotFound:
            pass
        exit(0)

def printCompletionScript():
    script_dir = ph.dirname(ph.abspath(__file__))
    with open(f'{script_dir}/autocomplete/autocomplete.sh', 'r', encoding='utf-8') as f:
        print(f.read())

def parse_logging_settings(args):
    if args.quite or args.quite_all:
        logging.disable(logging.CRITICAL)
    if args.quite_all:
        executionEngine.disableOutput()
    if args.pretty:
        executionEngine.set_logging(args.pretty)

def main():
    iscomplete()
    try:
        loggingSetup()
        start()
        logging.info('Finishing myrunner')
        return 0
    except runnerExceptions.BaseMyRunnerException as err:
        err.pretty_output()
        logging.info('Finishing myrunner')
        return err.return_code

def start():  # noqa: C901
    args = arg_parser.parse()
    if args.completion:
        printCompletionScript()
        exit(0)
    if args.version:
        getversion()
        return 0
    logging.info('Starting myrunner')
    # if args.docker:
    #     docker = DockerInteraction(args.docker)
    #     hclReader = HclReader((docker.get_runlist_from_container()))
    #     docker.command(hclReader.getruns()['send_request']['command'], {})
    if args.user_runlist:
        if (home := ph.expanduser('~')) is None:
            logging.error("Failed to get home path")
            return 1
        args.file = home + '/.' + args.file
    hclReader = HclReader(args.file)
    parse_logging_settings(args)
    runs = hclReader.getruns()
    settings = hclReader.getsettings()
    if args.describe:
        printRunListDescribe(args.file, settings.get('description', ''))
        printRunsTable(runs, args.runs)
        return 0
    if args.interactive or settings.get('interactive', False):
        executionEngine.ExecutionEngine.interactiveInput = True
        logging.debug('interactive')
    imports = hclReader.getimports()
    for run in args.runs:
        commandRun(runs, run, imports)
    return 0

def loggingSetup():
    # note: critical is not used
    logging.getLogger('myrunner')
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')


if __name__ == '__main__':
    exit(main())
