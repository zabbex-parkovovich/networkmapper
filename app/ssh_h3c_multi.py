import paramiko
import sys
import time

def ssh_exec_commands(host, port, username, password, commands, timeout=30):
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
        channel.get_pty()  # Нужно для интерактивных команд (system-view)
        channel.invoke_shell()

        # Отправляем все команды последовательно
        output = []
        for cmd in commands:
            cmd = cmd.strip()
            if not cmd:
                continue
            channel.send(cmd + '\n')
            time.sleep(0.5)  # Ждём выполнения
            # Читаем вывод до следующего приглашения (адаптируйте под свою систему)
            # Для простоты ждём фиксированное время и читаем всё
            time.sleep(1)
            while channel.recv_ready():
                output.append(channel.recv(65535).decode('utf-8', errors='ignore'))

        # Добираем остатки
        while channel.recv_ready():
            output.append(channel.recv(65535).decode('utf-8', errors='ignore'))

        return '\n'.join(output), '', 0

    except Exception as e:
        return '', str(e), 1
    finally:
        transport.close()

if __name__ == '__main__':
    if len(sys.argv) < 6:
        print("Usage: python ssh_h3c_multi.py <host> <port> <username> <password> <command1> [<command2> ...]")
        sys.exit(1)
    host = sys.argv[1]
    port = int(sys.argv[2])
    username = sys.argv[3]
    password = sys.argv[4]
    commands = sys.argv[5:]  # все последующие аргументы считаются командами
    out, err, code = ssh_exec_commands(host, port, username, password, commands)
    if code == 0:
        print(out)
        if err:
            print(err, file=sys.stderr)
    else:
        print(err, file=sys.stderr)
        sys.exit(code)
