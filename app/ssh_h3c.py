import paramiko
import sys

def ssh_exec(host, port, username, password, command, timeout=30):
    transport = paramiko.Transport((host, port))
    transport.sock.settimeout(timeout)
    try:
        # Разрешаем старые алгоритмы ключей хоста
        transport._preferred_keys = ['ssh-rsa', 'ssh-dss']
        # Подключаемся с паролем
        transport.connect(username=username, password=password)
        channel = transport.open_session()
        channel.exec_command(command)
        out = channel.recv(65535).decode('utf-8', errors='ignore')
        err = channel.recv_stderr(65535).decode('utf-8', errors='ignore')
        return out, err, 0
    except Exception as e:
        return '', str(e), 1
    finally:
        transport.close()

if __name__ == '__main__':
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
