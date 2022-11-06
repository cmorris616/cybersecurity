import os
import subprocess

from operations.recon_operation import ReconOperation
from output import Output
from utils import get_url_variations


class HttrackOperation(ReconOperation):
    def execute(self, args, output: Output):
        url_list = get_url_variations(args.url)

        for url in url_list:
            url_output_dir = os.path.join(args.dir, 'httrack')

            if not os.path.exists(url_output_dir):
                os.mkdir(url_output_dir)

            if '://' in url:
                url_output_dir = os.path.join(url_output_dir, url[url.index('://') + 3:])

            if not os.path.exists(url_output_dir):
                os.mkdir(url_output_dir)

            proc_args = ['httrack', url, '--urlhack', '--update', '--robots=3', '-O', url_output_dir]

            if args.proxy:
                proc_args.extend(['-P', args.proxy])

            subprocess.run(proc_args)

    def validate(self, args):
        pass
