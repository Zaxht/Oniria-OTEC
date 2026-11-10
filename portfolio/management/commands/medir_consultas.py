from django.core.management.base import BaseCommand
from django.db import connection
from django.test.utils import CaptureQueriesContext
from portfolio.models import Curso
from portfolio.views import cursos_relacionados


class Command(BaseCommand):
    help = 'Compara las consultas de diez cursos con y sin optimización de relaciones.'

    def handle(self, *args, **options):
        for nombre, qs in [('Sin optimizar', Curso.objects.all()), ('Optimizado', cursos_relacionados())]:
            with CaptureQueriesContext(connection) as consultas:
                for curso in qs[:10]:
                    str(curso.area)
                    str(curso.relator)
                    list(curso.competencias.all())
            self.stdout.write(f'{nombre}: {len(consultas)} consultas')
