from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone


class Area(models.Model):
    nombre = models.CharField('nombre', max_length=100, unique=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'área de capacitación'
        verbose_name_plural = 'áreas de capacitación'

    def __str__(self):
        return self.nombre


class Competencia(models.Model):
    nombre = models.CharField('nombre', max_length=100, unique=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Curso(models.Model):
    class Modalidad(models.TextChoices):
        PRESENCIAL = 'presencial', 'Presencial'
        ONLINE = 'online', 'Online'
        MIXTA = 'mixta', 'Mixta'

    nombre = models.CharField(max_length=160)
    descripcion = models.TextField('descripción')
    horas = models.PositiveSmallIntegerField('horas totales', validators=[MinValueValidator(4), MaxValueValidator(200)])
    cupos = models.PositiveSmallIntegerField(validators=[MinValueValidator(5), MaxValueValidator(60)])
    modalidad = models.CharField(max_length=12, choices=Modalidad.choices)
    fecha_inicio = models.DateField('fecha de inicio')
    creado = models.DateTimeField(auto_now_add=True)
    relator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cursos')
    area = models.ForeignKey(Area, verbose_name='área', on_delete=models.SET_NULL, null=True, blank=True, related_name='cursos')
    competencias = models.ManyToManyField(Competencia, blank=True, related_name='cursos')

    class Meta:
        ordering = ['-creado', '-pk']
        constraints = [
            models.CheckConstraint(condition=models.Q(horas__gte=4, horas__lte=200), name='curso_horas_rango'),
            models.CheckConstraint(condition=models.Q(cupos__gte=5, cupos__lte=60), name='curso_cupos_rango'),
        ]

    def __str__(self):
        return self.nombre

    @property
    def iniciado(self):
        return self.fecha_inicio < timezone.localdate()


class Matricula(models.Model):
    class Estado(models.TextChoices):
        SOLICITADA = 'solicitada', 'Solicitada'
        CONFIRMADA = 'confirmada', 'Confirmada'
        ANULADA = 'anulada', 'Anulada'

    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='matriculas')
    participante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='matriculas')
    empresa = models.CharField(max_length=160)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.SOLICITADA)

    class Meta:
        ordering = ['-fecha', '-pk']
        verbose_name = 'matrícula'
        constraints = [models.UniqueConstraint(fields=['curso', 'participante'], name='matricula_unica')]

    def __str__(self):
        return f'{self.participante} · {self.curso}'

    def clean(self):
        super().clean()
        if self.curso_id and self.participante_id:
            if self.curso.relator_id == self.participante_id:
                raise ValidationError('No puedes matricularte en tu propio curso.')
            if self._state.adding and self.curso.iniciado:
                raise ValidationError('Este curso ya comenzó. No admite nuevas matrículas.')
