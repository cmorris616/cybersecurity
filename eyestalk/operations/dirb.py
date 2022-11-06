import os
import subprocess

from operations.recon_operation import ReconOperation
from output import Output
from utils import get_url_variations


class DirBOperation(ReconOperation):
    def execute(self, args, output: Output):
        url_list = get_url_variations(args.url)

        for url in url_list:
            url_output_file = os.path.join(args.dir, 'dirb')

            if not os.path.exists(url_output_file):
                os.mkdir(url_output_file)

            if '://' in url:
                url_output_file = os.path.join(url_output_file, url[url.index('://') + 3:] + '.log')

            proc_args = ['dirb', url, '-o', url_output_file]

            if args.proxy:
                proc_args.extend(['-p', args.proxy])

            subprocess.run(proc_args)

            result = DirbResult(url=url)

            with open(url_output_file, 'r') as results:
                line = results.readline()
                if line.startswith('+'):
                    dir = line[2:]
                    
                    result.dirs.append()

    def validate(self, args):
        pass


class DirbResult:
    def __init__(self, url=''):
        self.url = url
        self.dirs = []
