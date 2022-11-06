import argparse
import json
import logging
import os
import sys
from datetime import datetime

from operations.dirb import DirBOperation
from operations.httrack import HttrackOperation
from operations.nmap import NmapOperation
from output import Output

logger = logging.getLogger('eyestalk')
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler(stream=sys.stdout)
logger.setLevel(logging.INFO)
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)

operations = {
    'nmap': NmapOperation(name='NMap'),
    'httrack': HttrackOperation(name='Httrack'),
    'dirb': DirBOperation(name='DirB')
}

output = Output()
output.command_line = sys.executable + ' ' + ' '.join(sys.argv)

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

args.dir = os.path.join(args.dir, 'eyestalk', datetime.now().strftime('%Y%m%d%H%M%S'))

if not os.path.exists(args.dir):
    os.makedirs(args.dir, exist_ok=True)

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
        logger.error(f'Validation failed for {op.name}')
        exit(1)

    logger.info(f'Executing {op.name}')
    op.execute(args, output)

dat_file = os.path.join(args.dir, 'eyestalk.dat')
logger.info('Output data saved to ' + dat_file)

with open(dat_file, 'w') as output_dat:
    output_dat.write(json.dumps(output, indent=2))
