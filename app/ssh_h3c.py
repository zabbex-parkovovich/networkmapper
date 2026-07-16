import paramiko
import sys
import logging

# Настройка логирования (опционально)
logging.basicConfig(level=logging.INFO)

def ssh_exec(host, port, username, password, command, timeout=30):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, port, username, password, timeout=timeout)
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        out = stdout.read().decode('utf-8')
        err = stderr.read().decode('utf-8')
        return out, err, 0
    except Exception as e:
        return '', str(e), 1
    finally:
        client.close()

if __name__ == '__main__':
    # Параметры передаём через аргументы командной строки
    if len(sys.argv) < 6:
        print("Usage: python ssh_h3c.py <host> <port> <username> <password> <command>")
        sys.exit(1)
    host = sys.argv[1]
    port = int(sys.argv[2])
    username = sys.argv[3]
    password = sys.argv[4]
    command = sys.argv[5]
    out, err, code = ssh_exec(host, port, username, password, command)
    if code == 0:
        print(out)
        if err:
            print(err, file=sys.stderr)
    else:
        print(err, file=sys.stderr)
        sys.exit(code)
