from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.utils.http import url_has_allowed_host_and_scheme
from django.http import JsonResponse
from .forms import AreaForm, CursoForm, MatriculaForm, PerfilForm, RegistroForm
from .models import Area, Curso, Matricula
from .course_guides import guide_for


def cursos_relacionados():
    # Cápsula N+1: FK en JOIN y competencias en una consulta adicional.
    return Curso.objects.select_related('area', 'relator').prefetch_related('competencias')


def portfolio_home(request):
    if request.user.is_authenticated:
        return redirect('cuenta')
    return render(request, 'home.html', {
        'cursos': cursos_relacionados()[:4],
        'total_cursos': Curso.objects.count(), 'total_areas': Area.objects.count(),
        'total_matriculas': Matricula.objects.filter(estado=Matricula.Estado.CONFIRMADA).count(),
    })


def curso_lista(request):
    qs = cursos_relacionados()
    q = request.GET.get('q', '').strip()
    area = request.GET.get('area', '')
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
    if area.isascii() and area.isdigit() and len(area) <= 18:
        qs = qs.filter(area_id=int(area))
    elif area:
        qs = qs.none()
    params = request.GET.copy()
    params.pop('page', None)
    return render(request, 'curso_lista.html', {
        'page_obj': Paginator(qs, 5).get_page(request.GET.get('page')),
        'areas': Area.objects.all(), 'q': q, 'area_actual': area,
        'querystring': params.urlencode(),
    })


def curso_detalle(request, pk):
    curso = get_object_or_404(cursos_relacionados(), pk=pk)
    matricula = None
    if request.user.is_authenticated:
        matricula = Matricula.objects.filter(curso=curso, participante=request.user).first()
    return render(request, 'curso_detalle.html', {
        'curso': curso, 'matricula': matricula, 'guide': guide_for(curso),
        'otros_cursos': cursos_relacionados().exclude(pk=curso.pk)[:6],
    })


def comprobar_dueno(curso, usuario):
    if curso.relator_id != usuario.pk:
        raise PermissionDenied('Solo el relator de este curso puede realizar esta acción.')


@login_required
@permission_required('portfolio.add_curso', raise_exception=True)
def curso_crear(request):
    form = CursoForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        curso = form.save(commit=False)
        curso.relator = request.user
        curso.save()
        form.save_m2m()
        messages.success(request, 'Curso publicado correctamente.')
        return redirect('curso_detalle', pk=curso.pk)
    return render(request, 'formulario.html', {'form': form, 'titulo': 'Publicar un curso', 'es_curso': True})


@login_required
def curso_editar(request, pk):
    curso = get_object_or_404(Curso, pk=pk)
    comprobar_dueno(curso, request.user)
    form = CursoForm(request.POST if request.method == 'POST' else None, instance=curso)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Curso actualizado correctamente.')
        return redirect('curso_detalle', pk=curso.pk)
    return render(request, 'formulario.html', {'form': form, 'titulo': 'Editar curso', 'es_curso': True})


@login_required
def curso_eliminar(request, pk):
    curso = get_object_or_404(Curso, pk=pk)
    comprobar_dueno(curso, request.user)
    if request.method == 'POST':
        curso.delete()
        messages.success(request, 'Curso y sus matrículas eliminados.')
        return redirect('mis_cursos')
    return render(request, 'confirmar_eliminacion.html', {'curso': curso})


@login_required
@permission_required('portfolio.add_curso', raise_exception=True)
def mis_cursos(request):
    return render(request, 'mis_cursos.html', {'cursos': cursos_relacionados().filter(relator=request.user)})


@login_required
@permission_required('portfolio.add_area', raise_exception=True)
def area_crear(request):
    form = AreaForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Área creada. Ya puedes seleccionarla al publicar o editar cursos.')
        return redirect('curso_lista')
    return render(request, 'formulario.html', {'form': form, 'titulo': 'Crear área de capacitación'})


def registro(request):
    if request.user.is_authenticated:
        return redirect('cuenta')
    form = RegistroForm(request.POST if request.method == 'POST' else None)
    destino = request.POST.get('next', request.GET.get('next', ''))
    if request.method == 'POST' and form.is_valid():
        usuario = form.save()
        login(request, usuario)
        messages.success(request, 'Tu cuenta está lista. Encuentra tu primer curso para explorar.')
        respuesta = redirect(destino) if destino and url_has_allowed_host_and_scheme(destino, allowed_hosts={request.get_host()}, require_https=request.is_secure()) else redirect('cuenta')
        if request.headers.get('X-Oniria-Modal') == '1':
            return JsonResponse({'redirect': respuesta.url})
        return respuesta
    template = 'registration/auth_fragment.html' if request.headers.get('X-Oniria-Modal') == '1' else 'registration/auth_page.html'
    return render(request, template, {'form': form, 'auth_mode': 'register', 'next': destino})


@login_required
def cuenta(request):
    matriculas = request.user.matriculas.all()
    resumen = matriculas.aggregate(total=Count('pk'), activas=Count('pk', filter=~Q(estado=Matricula.Estado.ANULADA)))
    return render(request, 'cuenta.html', {
        'nombre_personal': request.user.first_name or request.user.username.split('@')[0],
        'total_cursos': request.user.cursos.count(), 'total_matriculas': resumen['total'],
        'matriculas_activas': resumen['activas'],
        'pendientes_recibidas': Matricula.objects.filter(curso__relator=request.user, estado=Matricula.Estado.SOLICITADA).count(),
        'cursos_personales': cursos_relacionados().filter(relator=request.user)[:3],
        'matriculas_recientes': matriculas.exclude(estado=Matricula.Estado.ANULADA).select_related('curso')[:3],
    })


@login_required
def perfil_editar(request):
    form = PerfilForm(request.POST if request.method == 'POST' else None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Tus datos fueron actualizados.')
        return redirect('cuenta')
    return render(request, 'formulario.html', {'form': form, 'titulo': 'Editar mis datos'})


class CambiarClaveView(LoginRequiredMixin, SuccessMessageMixin, PasswordChangeView):
    template_name = 'formulario.html'
    success_url = reverse_lazy('cuenta')
    success_message = 'Contraseña actualizada. Tu sesión sigue activa.'
    extra_context = {'titulo': 'Cambiar contraseña'}


class IngresarView(SuccessMessageMixin, LoginView):
    template_name = 'registration/auth_page.html'
    success_message = 'Sesión iniciada. Bienvenido a OTEC.'
    extra_context = {'auth_mode': 'login'}

    def get_template_names(self):
        if self.request.headers.get('X-Oniria-Modal') == '1':
            return ['registration/auth_fragment.html']
        return [self.template_name]

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        if self.request.headers.get('X-Oniria-Modal') == '1':
            return JsonResponse({'redirect': respuesta.url})
        return respuesta


class SalirView(LogoutView):
    def post(self, request, *args, **kwargs):
        respuesta = super().post(request, *args, **kwargs)
        messages.success(request, 'Sesión cerrada correctamente.')
        return respuesta


@login_required
def matricular(request, pk):
    curso = get_object_or_404(Curso, pk=pk)
    matricula = Matricula(curso=curso, participante=request.user)
    form = MatriculaForm(request.POST if request.method == 'POST' else None, instance=matricula)
    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic():
                matricula.full_clean()
                matricula.save()
        except ValidationError as error:
            form.add_error(None, error)
        except IntegrityError:
            form.add_error(None, 'Ya tienes una matrícula en este curso.')
        else:
            messages.success(request, 'Matrícula solicitada. El relator revisará tu solicitud.')
            return redirect('mis_matriculas')
    return render(request, 'formulario.html', {
        'form': form, 'titulo': f'Matricularme en {curso.nombre}', 'boton': 'Solicitar matrícula',
    })


@login_required
def mis_matriculas(request):
    matriculas = Matricula.objects.filter(participante=request.user).select_related('curso', 'curso__relator')
    return render(request, 'matriculas.html', {'matriculas': matriculas, 'recibidas': False})


@login_required
@permission_required('portfolio.add_curso', raise_exception=True)
def matriculas_recibidas(request):
    matriculas = Matricula.objects.filter(curso__relator=request.user).select_related('curso', 'participante')
    return render(request, 'matriculas.html', {'matriculas': matriculas, 'recibidas': True})


@login_required
@require_POST
def matricula_cancelar(request, pk):
    with transaction.atomic():
        matricula = get_object_or_404(Matricula.objects.select_for_update(), pk=pk)
        if matricula.participante_id != request.user.pk:
            raise PermissionDenied
        if matricula.estado != Matricula.Estado.SOLICITADA:
            messages.error(request, 'Solo puedes cancelar matrículas que siguen solicitadas.')
        else:
            matricula.estado = Matricula.Estado.ANULADA
            matricula.save(update_fields=['estado'])
            messages.success(request, 'Matrícula cancelada.')
    return redirect('mis_matriculas')


@login_required
@require_POST
def matricula_estado(request, pk):
    with transaction.atomic():
        matricula = get_object_or_404(Matricula.objects.select_for_update().select_related('curso'), pk=pk)
        comprobar_dueno(matricula.curso, request.user)
        estado = request.POST.get('estado')
        if estado not in (Matricula.Estado.CONFIRMADA, Matricula.Estado.ANULADA):
            messages.error(request, 'Selecciona un estado válido: confirmada o anulada.')
        elif estado == Matricula.Estado.CONFIRMADA and matricula.participante_id == matricula.curso.relator_id:
            messages.error(request, 'No puedes confirmar una matrícula en tu propio curso.')
        else:
            matricula.estado = estado
            matricula.save(update_fields=['estado'])
            messages.success(request, f'Matrícula {matricula.get_estado_display().lower()}.')
    return redirect('matriculas_recibidas')
