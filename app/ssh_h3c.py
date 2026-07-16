import paramiko
import sys

def ssh_exec(host, port, username, password, command, timeout=30):
    transport = paramiko.Transport((host, port))
    transport.sock.settimeout(timeout)
    try:
        # Регистрируем поддержку устаревших алгоритмов ключей хоста
        transport._key_info = {
            'ssh-rsa': paramiko.RSAKey,
            'ssh-dss': paramiko.DSSKey,
            'ecdsa-sha2-nistp256': paramiko.ECDSAKey,
            'ecdsa-sha2-nistp384': paramiko.ECDSAKey,
            'ecdsa-sha2-nistp521': paramiko.ECDSAKey,
            'ssh-ed25519': paramiko.Ed25519Key,
        }
        # Указываем предпочитаемые алгоритмы (порядок важен)
        transport._preferred_keys = ['ssh-rsa', 'ssh-dss']
        # Подключаемся
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
