import paramiko
import sys
import logging

# Можно включить логирование для отладки
logging.basicConfig(level=logging.INFO)

def ssh_exec(host, port, username, password, command, timeout=30):
    client = paramiko.SSHClient()
    # Разрешаем автоматически добавлять ключ хоста (но это не решает проблему алгоритма)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        # ВАЖНО: явно указываем, какие алгоритмы ключей хоста мы принимаем
        client.connect(
            host, port, username, password, timeout=timeout,
            hostkey_algorithms=['ssh-rsa', 'ssh-dss', 'ecdsa-sha2-nistp256']
        )
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        out = stdout.read().decode('utf-8', errors='ignore')
        err = stderr.read().decode('utf-8', errors='ignore')
        return out, err, 0
    except Exception as e:
        return '', str(e), 1
    finally:
        client.close()

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
