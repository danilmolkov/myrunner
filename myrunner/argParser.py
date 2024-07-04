import argparse

def parse():
    """
    Parse command line arguments
    """

    parser = argparse.ArgumentParser(
        prog='myRunner', description='Perform runs', epilog='In developing. Author: molkovdanil@gmail.com')

    parser.add_argument('-f', '--file', type=str,
                        default='runlist.hcl', help='Path to file with runs')
    parser.add_argument('-d', '--describe', dest='describe', action='store_true',
                        help='Show description about runs in --file for input runs (or for all if empty)')
    parser.add_argument('runs', metavar='run', nargs='*',
                        help='run to command', default=[])
    parser.add_argument('-v', '--version', dest='version', action='store_true',
                        help='print version of myrunner')
    parser.add_argument('-q', '--quite', dest='quite', action='store_true', help='print only runs output')
    parser.add_argument('-qq', '--quite-all', dest='quite_all', action='store_true', help='don\'t print any output')
    parser.add_argument('-i', '--interactive', dest='interactive', action='store_true', help='(experimental!) ask interactively about executing and environment variables')

    return parser.parse_args()
