"""Prepara una instancia MySQL local y aislada. No modifica servicios existentes."""
import argparse
import json
import secrets
import socket
import subprocess
import time
from pathlib import Path

import MySQLdb

ROOT = Path(__file__).resolve().parent.parent
LOCAL = ROOT / '.local'
DATA = LOCAL / 'mysql'
PORT = 3307


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mysqld', default=r'C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld.exe')
    args = parser.parse_args()
    if (ROOT / '.env').exists() or DATA.exists():
        raise SystemExit('Ya existe .env o .local/mysql. No se sobrescribió nada; usa iniciar_mysql.ps1.')
    with socket.socket() as probe:
        if probe.connect_ex(('127.0.0.1', PORT)) == 0:
            raise SystemExit('El puerto 3307 está ocupado. No se modificó el servidor existente.')
    if not Path(args.mysqld).is_file():
        raise SystemExit('No se encontró mysqld. Indica su ruta con --mysqld.')
    LOCAL.mkdir(exist_ok=True)
    DATA.mkdir()
    flags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
    result = subprocess.run([args.mysqld, '--no-defaults', '--initialize-insecure', f'--datadir={DATA}'],
                            capture_output=True, creationflags=flags)
    (LOCAL / 'initialize.log').write_bytes(result.stdout + result.stderr)
    if result.returncode:
        raise SystemExit('Falló la inicialización; consulta .local/initialize.log.')
    log = (LOCAL / 'mysql.log').open('ab')
    process = subprocess.Popen([args.mysqld, '--no-defaults', f'--datadir={DATA}', f'--port={PORT}',
        '--bind-address=127.0.0.1', '--mysqlx=0', '--console'], stdout=log, stderr=log, creationflags=flags)
    (LOCAL / 'mysql-process.json').write_text(json.dumps({'pid': process.pid, 'mysqld': args.mysqld, 'port': PORT}))
    for attempt in range(60):
        try:
            db = MySQLdb.connect(host='127.0.0.1', port=PORT, user='root', connect_timeout=1)
            break
        except MySQLdb.OperationalError:
            if process.poll() is not None:
                raise SystemExit('MySQL se detuvo. Consulta .local/mysql.log.')
            time.sleep(0.5)
    else:
        raise SystemExit('MySQL no respondió a tiempo. Consulta .local/mysql.log.')
    root_password = secrets.token_urlsafe(32)
    app_password = secrets.token_urlsafe(32)
    # Guardar la clave local antes del cambio permite recuperar un fallo de provisión.
    (LOCAL / 'mysql-admin.json').write_text(json.dumps({'user': 'root', 'password': root_password, 'port': PORT}))
    cursor = db.cursor()
    cursor.execute("ALTER USER 'root'@'localhost' IDENTIFIED BY %s", (root_password,))
    cursor.execute('CREATE DATABASE otec CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
    cursor.execute("CREATE USER 'otec'@'localhost' IDENTIFIED BY %s", (app_password,))
    cursor.execute("GRANT ALL PRIVILEGES ON otec.* TO 'otec'@'localhost'")
    cursor.execute("GRANT ALL PRIVILEGES ON `test\\_otec`.* TO 'otec'@'localhost'")
    db.close()
    (LOCAL / 'mysql-admin.json').write_text(json.dumps({'user': 'root', 'password': root_password, 'port': PORT}))
    (ROOT / '.env').write_text(
        f'DJANGO_DEBUG=True\nDJANGO_SECRET_KEY={secrets.token_urlsafe(48)}\n'
        'DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1\nDB_NAME=otec\nDB_USER=otec\n'
        f'DB_PASSWORD={app_password}\nDB_HOST=127.0.0.1\nDB_PORT={PORT}\n'
        f'OTEC_DEMO_PASSWORD={secrets.token_urlsafe(14)}\n', encoding='utf-8')
    print('MySQL OTEC listo en 127.0.0.1:3307. Configuración guardada en .env; credenciales locales excluidas de Git.')


if __name__ == '__main__':
    main()
