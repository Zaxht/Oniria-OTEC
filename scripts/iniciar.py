"""Arranca la instancia existente de MySQL y Django sin scripts de PowerShell."""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def puerto_abierto(host, port):
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False


def preparar_mysql():
    import django
    os.environ['DJANGO_SETTINGS_MODULE'] = 'miempresa.settings'
    django.setup()
    from django.db import connection, OperationalError

    config = connection.settings_dict
    host = config['HOST'] or '127.0.0.1'
    port = int(config['PORT'] or 3306)
    if not puerto_abierto(host, port):
        metadata = ROOT / '.local' / 'mysql-process.json'
        if not metadata.exists():
            raise RuntimeError('MySQL no responde. Inicia tu servidor MySQL y vuelve a intentarlo.')
        local = json.loads(metadata.read_text(encoding='utf-8-sig'))
        if host not in ('127.0.0.1', 'localhost') or port != local['port']:
            raise RuntimeError('El servidor configurado en .env no responde. No es la instancia local de OTEC.')
        executable = Path(local['mysqld'])
        data = ROOT / '.local' / 'mysql'
        if not executable.is_file() or not data.is_dir():
            raise RuntimeError('No se encontro el ejecutable o los datos de MySQL. Revisa README.md.')
        print('Iniciando MySQL OTEC...', flush=True)
        with (ROOT / '.local' / 'mysql-launcher.log').open('ab') as log:
            process = subprocess.Popen([
                str(executable), '--no-defaults', f'--datadir={data}', f'--port={port}',
                '--bind-address=127.0.0.1', '--mysqlx=0', '--console',
            ], stdout=log, stderr=log, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        local['pid'] = process.pid
        metadata.write_text(json.dumps(local), encoding='utf-8')
    # La apertura del puerto puede preceder a la disponibilidad de la base.
    for attempt in range(60):
        try:
            connection.ensure_connection()
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
            connection.close()
            print('MySQL conectado correctamente.', flush=True)
            return
        except OperationalError as error:
            connection.close()
            if error.args and error.args[0] not in (2002, 2003, 2006, 2013):
                raise RuntimeError('MySQL responde, pero no acepta la configuracion de .env. Revisa base, usuario y clave.') from error
            time.sleep(0.5)
    raise RuntimeError('MySQL no inicio a tiempo. Consulta .local/mysql-launcher.log.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Verifica MySQL sin iniciar Django.')
    args = parser.parse_args()
    os.chdir(ROOT)
    try:
        preparar_mysql()
        if args.check:
            return 0
        if puerto_abierto('127.0.0.1', 8000):
            print('El puerto 8000 ya esta en uso. Si OTEC ya esta abierto, visita http://127.0.0.1:8000/')
            print('Para usar este lanzador, cierra primero el servidor anterior con Ctrl+C.')
            return 0
        print('\nOTEC: http://127.0.0.1:8000/\nManten esta ventana abierta. Ctrl+C detiene Django.\n', flush=True)
        return subprocess.call([sys.executable, 'manage.py', 'runserver', '127.0.0.1:8000'])
    except KeyboardInterrupt:
        print('\nServidor detenido.')
        return 0
    except (RuntimeError, OSError, ValueError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
