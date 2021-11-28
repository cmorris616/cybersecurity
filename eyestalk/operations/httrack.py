import os
import subprocess

from operations.recon_operation import ReconOperation
from utils import get_url_variations


class HttrackOperation(ReconOperation):
    def execute(self, args):
        url_list = get_url_variations(args.url)
        
        for url in url_list:
            url_output_dir = os.path.join(args.dir, 'httrack')

            if not os.path.exists(url_output_dir):
                os.mkdir(url_output_dir)

            if '://' in url:
                url_output_dir = os.path.join(url_output_dir, url[url.index('://') + 3:])

            if not os.path.exists(url_output_dir):
                os.mkdir(url_output_dir)

            subprocess.run(['httrack', url, '--urlhack', '--robots=3', '-O', url_output_dir])

    def validate(self, args):
        pass
