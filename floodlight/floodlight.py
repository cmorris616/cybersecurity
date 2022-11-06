'''
This application will reach out to HackerOne to pull
potential targets.  Those targets will then be written
to a file.  The file will be read and the targets will
be scanned.  The targets and scan results will be
written to a database.
'''

from datetime import datetime
import logging
import os
from floodlight.models.models import Host, Log4jScanResult, NmapResult
from floodlight import get_engine, TARGET_FILE
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_

from floodlight.acquire_targets import query_directory

try:

    # query_directory()

    Session = sessionmaker(bind=get_engine())
    session = Session()

    existing_hosts = session.query(Host)

    def output_message(message):
        total_length = len(message) + 4

        logging.info('*' * total_length)
        logging.info(f'* {message} *')
        logging.info('*' * total_length)

    def scan_target(target=''):
        ###############
        # User inputs #
        ###############
        if target is None or target == '':
            workspace_folder = input('Workspace Folder: ')
            target_host = input('Target Host: ')
        else:
            workspace_folder = target
            target_host = target

        ###############
        # Directories #
        ###############
        HOME_DIRECTORY = os.environ['HOME']
        WORKSPACE_BASE = f'{HOME_DIRECTORY}/cybersecurity/bountyhunting'
        TOOLS_DIR = f'{HOME_DIRECTORY}/cybersecurity/tools'
        WORKSPACE = os.path.join(WORKSPACE_BASE, workspace_folder)
        LOG4J_DIR = os.path.join(TOOLS_DIR, 'log4j-scan')
        LOG4J_VENV_DIR = os.path.join(TOOLS_DIR, 'log4j-scan-env')

        ############
        # Commands #
        ############
        NMAP_COMMAND = '/usr/bin/nmap'
        LOG4J_PYTHON_CMD = os.path.join(LOG4J_VENV_DIR, 'bin/python3')
        SUBLIST3R_COMMAND = '/usr/bin/sublist3r'

        ################
        # Output files #
        ################
        target_urls_file = os.path.join(
            WORKSPACE, f'target_urls_{target_host}.txt')

        ##########################################
        # Create workspace (if it doesn't exist) #
        ##########################################
        output_message("Creating workspace (if it doesn't exist)")
        os.makedirs(WORKSPACE, exist_ok=True)

        #############
        # Sublist3r #
        #############
        output_message('Gathering subdomains')

        import sublist3r

        subdomains = sublist3r.main(
            target_host, 10, None, None, False, False, False, None)

        global existing_hosts

        if target_host not in existing_hosts:
            output_message(f'Adding host: {target_host}')
            parent_host = Host()
            parent_host.host_name = target_host
            parent_host.last_seen = datetime.now()
            session.add(parent_host)
        else:
            parent_host = [
                x for x in existing_hosts if x.host_name == target_host.lower()][0]
            parent_host.last_seen = datetime.now()

        session.commit()

        parent_id = parent_host.id

        for subdomain in subdomains:
            if subdomain.lower() not in existing_hosts:
                output_message(f'Adding subdomain: {subdomain}')
                host = Host()
                host.host_name = subdomain.lower()
                host.parent_id = parent_id
                host.last_seen = datetime.now()

        existing_hosts = session.query(Host).filter(
            or_(Host.id == parent_id, Host.parent_id == parent_id))

        ############################
        # Create target URL's file #
        ############################
        output_message("Creating target URL's list")

        with open(target_urls_file, 'w+') as target_file:
            for host in existing_hosts:
                target_file.write(f'http://{host.host_name}\n')
                target_file.write(f'https://{host.host_name}\n')

        output_message(f"Target URL's file created at: '{target_urls_file}'")

        ########
        # NMap #
        ########
        output_message('Scanning for open ports')

        from nmap3 import nmap3
        import json
        nmap = nmap3.Nmap()

        for host in existing_hosts:
            domain = host.host_name
            print(f"Scanning '{domain}'")

            nmap_results = nmap.nmap_version_detection(
                domain, arg='-sV -Pn', args="--script vulners --script-args mincvss+5.0")

            result_iter = iter(nmap_results.keys())

            ip_address = next(result_iter)

            if 'ports' in nmap_results[ip_address]:
                ports = nmap_results[ip_address]['ports']
            else:
                ports = []

            for port in ports:
                nmap_result_record = NmapResult()
                nmap_result_record.host_id = host.id
                nmap_result_record.port = port['portid']
                nmap_result_record.protocol = port['protocol']

                service = port.get('service', {})
                nmap_result_record.service = service.get('name', '') + \
                    '(' + service.get('product', '') + ')'
                nmap_result_record.state = port['state']
                nmap_result_record.details = json.dumps(nmap_results)
                nmap_result_record.last_seen = datetime.now()

                session.commit()

        ##############
        # Log4J scan #
        ##############
        output_message('Scanning for Log4J vulnerabilities')
        LOG4J_LOG = 'log4j.log'

        for host in existing_hosts:
            if os.path.exists(LOG4J_LOG):
                os.remove(LOG4J_LOG)

            log4j_cmd = f'{LOG4J_PYTHON_CMD} "{LOG4J_DIR}/log4j-scan.py" -u "{host.host_name}" --headers-file "{LOG4J_DIR}/headers-large.txt" --run-all-tests --waf-bypass --disable-tls-to-register-dns 2>&1 > "{LOG4J_LOG}"'
            output_message(log4j_cmd)
            os.system(log4j_cmd)

            with open(LOG4J_LOG) as output_file:
                scan_output = output_file.readlines()

            log4j_scan_result = Log4jScanResult()
            log4j_scan_result.host_id = host.id
            log4j_scan_result.command = log4j_cmd
            log4j_scan_result.output = "".join(scan_output)
            log4j_scan_result.scan_date_time = datetime.now()

            session.add(log4j_scan_result)

            session.commit()

    if __name__ == '__main__':
        file_name = TARGET_FILE

        if not os.path.exists(file_name):
            print(f'"{file_name}" not found')
            exit(1)

        target_host = ''
        host_list = None

        while True:
            output_message(f'Reading targets from "{file_name}"')
            with open(file_name, 'r') as target_host_file:
                target_host = target_host_file.readline().replace('\n', '')

            if target_host is None or target_host == '':
                break

            output_message(f'Scanning {target_host}')
            scan_target(target=target_host)

            with open(file_name, 'r') as target_host_file:
                host_list = target_host_file.read().split('\n')

            host_list = [x for x in host_list if x.replace(
                '\n', '') != target_host]

            with open(file_name, 'w') as target_host_file:
                target_host_file.write('\n'.join(host_list))
except Exception as e:
    logging.error('An error occurred', e)
