import paramiko
import sys
import time

def ssh_exec(host, port, username, password, command, timeout=30):
    transport = paramiko.Transport((host, port))
    transport.sock.settimeout(timeout)

    def _verify_key(*args, **kwargs):
        pass
    transport._verify_key = _verify_key

    try:
        transport._key_info = {'ssh-rsa': paramiko.RSAKey}
        transport._preferred_keys = ['ssh-rsa']
        transport.connect(username=username, password=password)
        channel = transport.open_session()
        channel.exec_command(command)

        out_data = b''
        err_data = b''
        # Читаем, пока канал открыт
        while True:
            if channel.recv_ready():
                out_data += channel.recv(65535)
            if channel.recv_stderr_ready():
                err_data += channel.recv_stderr(65535)
            if channel.exit_status_ready():
                break
            time.sleep(0.1)

        # Добираем остатки
        out_data += channel.recv(65535)
        err_data += channel.recv_stderr(65535)

        out = out_data.decode('utf-8', errors='ignore')
        err = err_data.decode('utf-8', errors='ignore')
        return out, err, channel.recv_exit_status()
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
