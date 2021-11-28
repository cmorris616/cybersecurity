import argparse
import logging
import os
import sys

from operations.httrack import HttrackOperation
from operations.nmap import NmapOperation

logger = logging.getLogger('eyestalk')
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler(stream=sys.stdout)
logger.setLevel(logging.INFO)
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)

operations = {
    'nmap': NmapOperation(name='NMap'),
    'httrack': HttrackOperation(name='Httrack')
}

arg_parser = argparse.ArgumentParser(description='Recon Script')
arg_parser.add_argument('--url', help='The url to recon')
arg_parser.add_argument('--dir', help='The location to store recon results')
arg_parser.add_argument('--proxy', help='The url for the proxy to use')
arg_parser.add_argument('--logging-level', help='The logging level for the application',
                        choices=['critical, error, warning, info, debug'], nargs=1)
arg_parser.add_argument('--logfile', help='The name of the file to which output is logged', nargs=1)

for key in operations:
    arg_parser.add_argument(f'--no-{operations[key].name.lower()}', action='store_true',
                            help=f'Do not execute the {operations[key].name} operation')

args = arg_parser.parse_args()

if not args.logging_level:
    args.logging_level = 'info'

logging_level = logging.getLevelName(args.logging_level.upper())
logger.setLevel(logging_level)

if not args.url:
    logger.error('The URL is required')
    arg_parser.print_help()

if args.dir:
    args.dir = os.path.abspath(args.dir)
else:
    args.dir = os.path.abspath('.')

if not os.path.exists(args.dir):
    logger.error(f'"{args.dir}" does not exist.')
    exit(1)

args.dir = os.path.join(args.dir, 'eyestalk')

if not os.path.exists(args.dir):
    os.mkdir(args.dir)

log_filename = os.path.join(args.dir, 'eyestalk.log')
file_handler = logging.FileHandler(filename=log_filename)
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)

logger.info(f'Output will be logged to file "{log_filename}" ({logging.getLevelName(logger.getEffectiveLevel())})')

args.url = args.url.lower()

for key in operations:
    op = operations[key]

    if args.__getattribute__(f'no_{op.name.lower()}'):
        continue

    logger.info(f'Validating {op.name}')

    if op.validate(args) is False:
        exit(1)

    logger.info(f'Executing {op.name}')
    # op.execute(args)
