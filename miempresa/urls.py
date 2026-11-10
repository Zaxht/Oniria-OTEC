from django.contrib import admin
from django.urls import path
from portfolio import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.portfolio_home, name='home'),
    path('cursos/', views.curso_lista, name='curso_lista'),
    path('cursos/nuevo/', views.curso_crear, name='curso_crear'),
    path('cursos/mios/', views.mis_cursos, name='mis_cursos'),
    path('cursos/<int:pk>/', views.curso_detalle, name='curso_detalle'),
    path('cursos/<int:pk>/editar/', views.curso_editar, name='curso_editar'),
    path('cursos/<int:pk>/eliminar/', views.curso_eliminar, name='curso_eliminar'),
    path('cursos/<int:pk>/matricular/', views.matricular, name='matricular'),
    path('areas/nueva/', views.area_crear, name='area_crear'),
    path('registro/', views.registro, name='registro'),
    path('ingresar/', views.IngresarView.as_view(), name='login'),
    path('salir/', views.SalirView.as_view(), name='logout'),
    path('cuenta/', views.cuenta, name='cuenta'),
    path('cuenta/editar/', views.perfil_editar, name='perfil_editar'),
    path('cuenta/clave/', views.CambiarClaveView.as_view(), name='cambiar_clave'),
    path('matriculas/', views.mis_matriculas, name='mis_matriculas'),
    path('matriculas/recibidas/', views.matriculas_recibidas, name='matriculas_recibidas'),
    path('matriculas/<int:pk>/cancelar/', views.matricula_cancelar, name='matricula_cancelar'),
    path('matriculas/<int:pk>/estado/', views.matricula_estado, name='matricula_estado'),
]
