from django.core.management.base import BaseCommand
from django.db import transaction
from portfolio.demo_catalogo import AREAS, COMPETENCIAS, CURSOS, LUCIDOS_ANTERIORES
from portfolio.models import Area, Competencia, Curso


class Command(BaseCommand):
    help = 'Sustituye seis cursos demo por el nuevo temario, conservando sus matrículas.'

    @transaction.atomic
    def handle(self, *args, **options):
        actualizados = 0
        for i, anterior in enumerate(LUCIDOS_ANTERIORES):
            nombre, descripcion, area, competencia = CURSOS[i]
            relator = ['demo_relator', 'demo_relatora'][i % 2]
            curso = Curso.objects.filter(nombre=anterior, relator__username=relator).first()
            if not curso:
                continue
            curso.nombre, curso.descripcion = nombre, descripcion
            curso.area = Area.objects.get_or_create(nombre=AREAS[area])[0]
            curso.save(update_fields=['nombre', 'descripcion', 'area'])
            curso.competencias.set([Competencia.objects.get_or_create(nombre=COMPETENCIAS[c])[0] for c in {competencia, 3}])
            actualizados += 1
        self.stdout.write(self.style.SUCCESS(f'{actualizados} cursos actualizados; IDs y matrículas conservados.'))
