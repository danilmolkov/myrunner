import argparse


def parse():
    """
    Parse command line arguments
    """

    parser = argparse.ArgumentParser(
        prog='myRunner', description='Perform runs', epilog='In developing')

    parser.add_argument('-f', '--file', type=str,
                        default='runlist.hcl', help='Path to file with runs')
    parser.add_argument('-d', '--describe', dest='describe', action='store_true',
                        help='Show description about runs in --file for input runs (or for all if empty)')
    parser.add_argument('runs', metavar='run', nargs='*',
                        help='run to run', default=[])
    return parser.parse_args()
