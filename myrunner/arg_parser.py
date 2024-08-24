"""
Argument parser module of myRunner
"""
import argparse
from .execution_logger import ExecutionLogger as el

def parse():
    """
    Parse command line arguments
    """

    parser = argparse.ArgumentParser(
        prog='myRunner', description='Perform runs',
        epilog='In developing. Author: molkovdanil@gmail.com')

    parser.add_argument('-f', '--file', type=str,
                        default='runlist.hcl', help='Path to file with runs')
    parser.add_argument('-d', '--describe', dest='describe', action='store_true',
                        help='Show description about runs in --file for input runs '
                             '(or for all if empty)')
    parser.add_argument('runs', metavar='run', nargs='*',
                        help='run to command', default=[])
    parser.add_argument('-v', '--version', dest='version', action='store_true',
                        help='print version of myrunner')
    parser.add_argument('-i', '--interactive', dest='interactive', action='store_true',
                        help='(experimental!) ask interactively '
                        'about running and environment variables')
    parser.add_argument('-u', '--user-runlist', dest='user_runlist', action='store_true',
                        help='use user runlist (~/.runlist.hcl) instead of'
                             'provided with -f or default')

    logging = parser.add_argument_group('logging')
    logging.add_argument('-q', '--quite', dest='quite', action='store_true',
                         help='print only runs output')
    logging.add_argument('-qq', '--quite-all', dest='quite_all', action='store_true',
                         help='do not print any output')
    logging.add_argument('--pretty', dest='pretty',
                         choices=el.allowed_modes, default='full-no-command',
                         help='enable pretty logging')

    other = parser.add_argument_group('other')
    other.add_argument('--completion', dest='completion', action='store_true',
                       help='print autocompletion script. '
                            'Use: source <(myrunner --completion) (add this to ~/.bashrc)')

    return parser.parse_args()
