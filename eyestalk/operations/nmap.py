import json
import logging
import os

from nmap3 import nmap3

from operations.recon_operation import ReconOperation

logger = logging.getLogger("nmap_operation")


class NmapOperation(ReconOperation):
    def __init__(self, name='', target_url=''):
        if name == '' or name is None:
            name = 'nmap'

        super().__init__(name, target_url)

    def execute(self, args):
        nmap = nmap3.Nmap()
        nmap_results = nmap.nmap_version_detection(target=args.url)
        print(json.dumps(nmap_results, indent=2))

        file_name = os.path.join(args.dir, 'nmap_results_raw.txt')
        append_comma = False

        if os.path.exists(file_name):
            append_comma = True

        with open(file_name, 'a') as results_file:
            if append_comma is True:
                results_file.write(',\n')
            results_file.write(json.dumps(nmap_results, indent=2))

        with open(os.path.join(args.dir, 'nmap_results_formatted.txt'), 'a') as results_file:
            header = f'NMap Results for {args.url}'
            results_file.write('-' * (len(header) + 2) + '\n')
            results_file.write(header + '\n')
            results_file.write('-' * (len(header) + 2) + '\n')

            ip_address = next(iter(nmap_results.keys()))
            ports = nmap_results[ip_address]['ports']

            results_file.write(f'Target: {nmap_results[ip_address]["hostname"][0]["name"]} ({ip_address})\n\n')
            results_file.write('Port      Protocol   State      Service\n')
            results_file.write('----      --------   -----      -------\n')

            for port in ports:
                results_file.write(port['portid'])
                results_file.write(' ' * (10 - len(port['portid'])))
                results_file.write(port['protocol'])
                results_file.write(' ' * (11 - len(port['protocol'])))
                results_file.write(port['state'])
                results_file.write(' ' * (11 - len(port['state'])))
                service = port['service']
                service_info = service['name']

                if "product" in service.keys():
                    service_info += f'/{service["product"]}'

                if "extrainfo" in service.keys():
                    service_info += f' ({service["extrainfo"]})'

                results_file.write(service_info)
                results_file.write('\n')

            results_file.write('\n\n')

    def validate(self, args):
        pass
