import os
from datetime import timedelta
from django.contrib.auth.models import User, Group, Permission
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.crypto import get_random_string
from portfolio.models import Area, Competencia, Curso, Matricula
from portfolio.demo_catalogo import AREAS, COMPETENCIAS, CURSOS


class Command(BaseCommand):
    help = 'Carga datos ficticios de OTEC sin borrar ni sobrescribir registros existentes.'

    @transaction.atomic
    def handle(self, *args, **options):
        password = os.getenv('OTEC_DEMO_PASSWORD') or get_random_string(18)
        usuarios = []
        creados = []
        creadores, _ = Group.objects.get_or_create(name='Creadores')
        creadores.permissions.add(*Permission.objects.filter(content_type__app_label='portfolio', codename__in=['add_curso', 'add_area']))
        for username, nombre, apellido in [
            ('demo_relator', 'Camila', 'Torres'),
            ('demo_participante', 'Diego', 'Rojas'),
            ('demo_relatora', 'Valentina', 'Soto'),
        ]:
            user, nuevo = User.objects.get_or_create(username=username, defaults={
                'email': f'{username}@example.com', 'first_name': nombre, 'last_name': apellido,
            })
            if nuevo:
                user.set_password(password)
                user.save()
                if username in ('demo_relator', 'demo_relatora'):
                    user.groups.add(creadores)
                creados.append(username)
            usuarios.append(user)
        areas = [Area.objects.get_or_create(nombre=n)[0] for n in AREAS]
        competencias = [Competencia.objects.get_or_create(nombre=n)[0] for n in COMPETENCIAS]
        datos = CURSOS
        cursos = []
        propietario = User.objects.filter(username='fer@fer.com').first()
        for i, (nombre, descripcion, area, competencia) in enumerate(datos):
            curso, nuevo = Curso.objects.get_or_create(nombre=nombre, relator=propietario or usuarios[0 if i % 2 == 0 else 2], defaults={
                'descripcion': descripcion, 'area': areas[area], 'horas': 16 + i * 4, 'cupos': 20 + i,
                'modalidad': ['online', 'presencial', 'mixta'][i % 3],
                'fecha_inicio': timezone.localdate() + timedelta(days=14 + i * 3),
            })
            if nuevo:
                curso.competencias.set([competencias[competencia], competencias[3]])
            cursos.append(curso)
        for i in range(5):
            Matricula.objects.get_or_create(curso=cursos[i], participante=usuarios[1], defaults={
                'empresa': 'Empresa de ejemplo', 'estado': ['solicitada', 'confirmada', 'anulada'][i % 3],
            })
        self.stdout.write(self.style.SUCCESS('Datos de demostración disponibles: 3 usuarios, 10 cursos, 3 áreas, 5 competencias y 5 matrículas.'))
        if creados:
            self.stdout.write('Cuentas nuevas: ' + ', '.join(creados))
            self.stdout.write('Contraseña de las cuentas nuevas: ' + password)
        else:
            self.stdout.write('Se conservaron las contraseñas y los registros existentes.')
