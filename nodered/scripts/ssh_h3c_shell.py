import paramiko
import sys
import time
import re

def ssh_exec_interactive(host, port, username, password, commands, timeout=30):
    transport = paramiko.Transport((host, port))
    transport.sock.settimeout(timeout)

    # Отключаем проверку ключа хоста (чтобы избежать ошибок с ssh-rsa)
    def _verify_key(*args, **kwargs):
        pass
    transport._verify_key = _verify_key
    transport._key_info = {'ssh-rsa': paramiko.RSAKey}
    transport._preferred_keys = ['ssh-rsa']

    try:
        transport.connect(username=username, password=password)
        channel = transport.open_session()
        # Запрашиваем псевдотерминал для интерактивности
        channel.get_pty()
        channel.invoke_shell()
        time.sleep(1)  # ждём инициализацию

        # Отключаем пагинацию один раз
        channel.send("screen-length disable\n")
        time.sleep(0.5)
        # Сбрасываем буфер
        while channel.recv_ready():
            channel.recv(65535)

        output = ""
        for cmd in commands:
            channel.send(cmd + "\n")
            time.sleep(0.5)
            data = ""
            while True:
                if channel.recv_ready():
                    data += channel.recv(65535).decode('utf-8', errors='ignore')
                # Ждём приглашения (заканчивается на > или #)
                if re.search(r'[#>]\s*$', data):
                    break
                time.sleep(0.1)
            output += data
        return output, "", 0
    except Exception as e:
        return "", str(e), 1
    finally:
        transport.close()

if __name__ == '__main__':
    if len(sys.argv) < 6:
        print("Usage: python ssh_h3c_shell.py <host> <port> <username> <password> <cmd1> [cmd2 ...]")
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
