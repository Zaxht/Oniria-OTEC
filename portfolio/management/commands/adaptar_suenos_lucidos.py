from django.core.management.base import BaseCommand
from django.db import transaction
from portfolio.demo_catalogo import AREAS, COMPETENCIAS, CURSOS, ANTERIORES
from portfolio.models import Area, Competencia, Curso


class Command(BaseCommand):
    help = 'Adapta los diez cursos demo originales conservando IDs y matrículas.'

    @transaction.atomic
    def handle(self, *args, **options):
        relatores = ['demo_relator', 'demo_relatora']
        for modelo, anteriores, nuevos in [
            (Area, ['Tecnología', 'Gestión', 'Seguridad'], AREAS),
            (Competencia, ['Excel', 'Trabajo en equipo', 'Prevención de riesgos', 'Comunicación', 'Herramientas digitales'], COMPETENCIAS),
        ]:
            for anterior, nuevo in zip(anteriores, nuevos):
                objeto = modelo.objects.filter(nombre=anterior).first()
                if objeto and not objeto.cursos.exclude(relator__username__in=relatores).exists() and not modelo.objects.filter(nombre=nuevo).exists():
                    objeto.nombre = nuevo
                    objeto.save(update_fields=['nombre'])
        areas = [Area.objects.get_or_create(nombre=n)[0] for n in AREAS]
        competencias = [Competencia.objects.get_or_create(nombre=n)[0] for n in COMPETENCIAS]
        actualizados = 0
        for i, (anterior, datos) in enumerate(zip(ANTERIORES, CURSOS)):
            nombre, descripcion, area, competencia = datos
            curso = Curso.objects.filter(nombre=anterior, relator__username=relatores[i % 2]).first()
            if curso:
                curso.nombre = nombre
                curso.descripcion = descripcion
                curso.area = areas[area]
                curso.save(update_fields=['nombre', 'descripcion', 'area'])
                curso.competencias.set([competencias[competencia], competencias[3]])
                actualizados += 1
        self.stdout.write(self.style.SUCCESS(f'{actualizados} cursos adaptados. IDs, fechas, cupos y matrículas conservados.'))
