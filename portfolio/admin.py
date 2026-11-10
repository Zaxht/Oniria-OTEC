from django.contrib import admin
from .forms import CursoForm
from .models import Area, Competencia, Curso, Matricula


class CursoAdminForm(CursoForm):
    class Meta(CursoForm.Meta):
        fields = '__all__'


@admin.register(Area, Competencia)
class CatalogoAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    list_filter = ['nombre']
    search_fields = ['nombre']


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    form = CursoAdminForm
    list_display = ['nombre', 'relator', 'area', 'modalidad', 'fecha_inicio', 'cupos']
    list_filter = ['area', 'modalidad', 'fecha_inicio']
    search_fields = ['nombre', 'descripcion', 'relator__username']
    list_select_related = ['relator', 'area']


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ['curso', 'participante', 'empresa', 'estado', 'fecha']
    list_filter = ['estado', 'fecha']
    search_fields = ['curso__nombre', 'participante__username', 'empresa']
    list_select_related = ['curso', 'participante']


admin.site.site_header = 'Oniria · Administración'
admin.site.site_title = 'Oniria'
admin.site.index_title = 'El espacio detrás de los sueños'
