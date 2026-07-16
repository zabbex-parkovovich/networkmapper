import paramiko
import sys
import time
import re

def ssh_exec_interactive(host, port, username, password, commands, timeout=30):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, port, username=username, password=password, timeout=timeout)
        channel = client.invoke_shell()
        time.sleep(1)  # ждём инициализацию

        # Отключаем пагинацию
        channel.send("screen-length disable\n")
        time.sleep(0.5)
        # Сбрасываем буфер
        while channel.recv_ready():
            channel.recv(65535)

        output = ""
        for cmd in commands:
            channel.send(cmd + "\n")
            time.sleep(0.5)  # даём время на выполнение

            # Читаем, пока не увидим приглашение (заканчивается на > или #)
            data = ""
            while True:
                if channel.recv_ready():
                    data += channel.recv(65535).decode('utf-8', errors='ignore')
                # Приглашение обычно в конце строки, возможно с пробелами
                if re.search(r'[#>]\s*$', data):
                    break
                time.sleep(0.1)
            output += data
        return output, "", 0
    except Exception as e:
        return "", str(e), 1
    finally:
        client.close()

if __name__ == '__main__':
    if len(sys.argv) < 6:
        print("Usage: python ssh_h3c_interactive.py <host> <port> <username> <password> <cmd1> [cmd2 ...]")
        sys.exit(1)
    host = sys.argv[1]
    port = int(sys.argv[2])
    username = sys.argv[3]
    password = sys.argv[4]
    commands = sys.argv[5:]
    out, err, code = ssh_exec_interactive(host, port, username, password, commands)
    if code == 0:
        print(out)
        if err:
            print(err, file=sys.stderr)
    else:
        print(err, file=sys.stderr)
        sys.exit(code)
