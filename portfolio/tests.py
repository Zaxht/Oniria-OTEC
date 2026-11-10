from datetime import timedelta
from django.contrib.auth.models import User, Permission
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from django.core.management import call_command
from io import StringIO
from .forms import CursoForm, PerfilForm, RegistroForm
from .models import Area, Competencia, Curso, Matricula
from .views import cursos_relacionados


class OtecTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.dueno = User.objects.create_user('relator', email='relator@example.com', password='ClavePrueba-482!')
        cls.otro = User.objects.create_user('alumno', email='alumno@example.com', password='ClavePrueba-482!')
        cls.tercero = User.objects.create_user('tercero', email='tercero@example.com', password='ClavePrueba-482!')
        cls.dueno.user_permissions.add(*Permission.objects.filter(content_type__app_label='portfolio', codename__in=['add_curso', 'add_area']))
        cls.area = Area.objects.create(nombre='Tecnología')
        cls.etiquetas = [Competencia.objects.create(nombre=f'Competencia {i}') for i in range(6)]
        cls.curso = Curso.objects.create(nombre='Excel inicial', descripcion='Aprende fórmulas y tablas', horas=20,
            cupos=10, modalidad='online', fecha_inicio=timezone.localdate() + timedelta(days=10),
            relator=cls.dueno, area=cls.area)
        cls.curso.competencias.set(cls.etiquetas[:2])

    def datos_curso(self, **cambios):
        datos = {'nombre': 'Curso nuevo', 'descripcion': 'Descripción del curso', 'horas': 20, 'cupos': 10,
                 'modalidad': 'online', 'fecha_inicio': str(timezone.localdate() + timedelta(days=20)),
                 'area': self.area.pk, 'competencias': [e.pk for e in self.etiquetas[:2]]}
        return datos | cambios

    def test_publico_y_detalle(self):
        for nombre, args in [('home', []), ('curso_lista', []), ('curso_detalle', [self.curso.pk])]:
            self.assertEqual(self.client.get(reverse(nombre, args=args)).status_code, 200)

    def test_temario_conserva_matriculas_y_no_modifica_cursos_ajenos(self):
        from .demo_catalogo import CURSOS, LUCIDOS_ANTERIORES
        call_command('seed_demo', stdout=StringIO())
        curso = Curso.objects.get(nombre=CURSOS[0][0], relator__username='demo_relator')
        curso.nombre = LUCIDOS_ANTERIORES[0]
        curso.save()
        self.curso.nombre = LUCIDOS_ANTERIORES[0]
        self.curso.save()
        antes = list(curso.matriculas.values_list('pk', 'estado'))
        total = Curso.objects.count()
        call_command('actualizar_temario_oniria', stdout=StringIO())
        call_command('actualizar_temario_oniria', stdout=StringIO())
        curso.refresh_from_db()
        self.curso.refresh_from_db()
        self.assertEqual(curso.nombre, CURSOS[0][0])
        self.assertEqual(list(curso.matriculas.values_list('pk', 'estado')), antes)
        self.assertEqual(self.curso.nombre, LUCIDOS_ANTERIORES[0])
        self.assertEqual(Curso.objects.count(), total)

    def test_carrusel_detalle_excluye_curso_actual(self):
        respuesta = self.client.get(reverse('curso_detalle', args=[self.curso.pk]))
        self.assertNotIn(self.curso.pk, [curso.pk for curso in respuesta.context['otros_cursos']])

    def test_login_modal_errores_y_redireccion(self):
        url = reverse('login')
        response = self.client.get(url, HTTP_X_ONIRIA_MODAL='1')
        self.assertContains(response, 'class="auth-form"')
        self.assertNotContains(response, '<html')
        response = self.client.post(url, {'username': 'alumno', 'password': 'incorrecta'}, HTTP_X_ONIRIA_MODAL='1')
        self.assertContains(response, 'errorlist')
        self.assertNotIn('_auth_user_id', self.client.session)
        response = self.client.post(url, {'username': 'alumno', 'password': 'ClavePrueba-482!', 'next': '/cursos/'}, HTTP_X_ONIRIA_MODAL='1')
        self.assertEqual(response.json(), {'redirect': '/cursos/'})
        self.assertContains(self.client.get('/cursos/'), 'Sesión iniciada')

    def test_registro_modal_valida_y_rechaza_destino_externo(self):
        url = reverse('registro')
        response = self.client.get(url, HTTP_X_ONIRIA_MODAL='1')
        self.assertContains(response, 'Crear mi cuenta')
        self.assertNotContains(response, '<html')
        datos = {'username': 'modal_nuevo', 'email': 'ALUMNO@example.com', 'password1': 'RegistroModal-824!', 'password2': 'RegistroModal-824!', 'next': 'https://example.org/'}
        response = self.client.post(url, datos, HTTP_X_ONIRIA_MODAL='1')
        self.assertContains(response, 'Este correo ya pertenece')
        self.assertFalse(User.objects.filter(username='modal_nuevo').exists())
        datos['email'] = 'modal@example.com'
        response = self.client.post(url, datos, HTTP_X_ONIRIA_MODAL='1')
        self.assertEqual(response.json(), {'redirect': reverse('cuenta')})
        self.assertContains(self.client.get(reverse('cuenta')), 'Tu cuenta está lista')
        self.assertIn('_auth_user_id', self.client.session)

    def test_seed_conserva_cursos_transferidos_a_fer(self):
        call_command('seed_demo', stdout=StringIO())
        fer = User.objects.create_user('fer@fer.com', email='fer@fer.com')
        Curso.objects.filter(relator__username__in=['demo_relator', 'demo_relatora']).update(relator=fer)
        total = Curso.objects.count()
        call_command('seed_demo', stdout=StringIO())
        self.assertEqual(Curso.objects.count(), total)
        self.assertEqual(fer.cursos.count(), 10)

    def test_anonimo_redirigido(self):
        for nombre, args in [('curso_crear', []), ('curso_editar', [self.curso.pk]),
                             ('curso_eliminar', [self.curso.pk]), ('cuenta', []), ('mis_matriculas', []),
                             ('matriculas_recibidas', []), ('area_crear', []), ('matricular', [self.curso.pk])]:
            self.assertEqual(self.client.get(reverse(nombre, args=args)).status_code, 302)

    def test_ajeno_get_y_post_da_403(self):
        self.client.force_login(self.otro)
        for accion in ['curso_editar', 'curso_eliminar']:
            url = reverse(accion, args=[self.curso.pk])
            self.assertEqual(self.client.get(url).status_code, 403)
            self.assertEqual(self.client.post(url, self.datos_curso()).status_code, 403)
        self.curso.refresh_from_db()
        self.assertEqual(self.curso.nombre, 'Excel inicial')

    def test_inexistente_da_404(self):
        self.client.force_login(self.dueno)
        self.assertEqual(self.client.get(reverse('curso_editar', args=[999999])).status_code, 404)

    def test_creacion_dueno_y_m2m(self):
        self.client.force_login(self.dueno)
        datos = self.datos_curso(relator=self.otro.pk)
        respuesta = self.client.post(reverse('curso_crear'), datos, follow=True)
        self.assertContains(respuesta, 'Curso publicado correctamente')
        curso = Curso.objects.get(nombre='Curso nuevo')
        self.assertEqual(curso.relator, self.dueno)
        self.assertEqual(curso.competencias.count(), 2)

    def test_editar_precarga_y_guarda_competencias(self):
        self.client.force_login(self.dueno)
        url = reverse('curso_editar', args=[self.curso.pk])
        self.assertEqual(len(self.client.get(url).context['form'].initial['competencias']), 2)
        self.client.post(url, self.datos_curso(competencias=[self.etiquetas[3].pk]))
        self.curso.refresh_from_db()
        self.assertEqual(list(self.curso.competencias.all()), [self.etiquetas[3]])

    def test_eliminar_requiere_post(self):
        self.client.force_login(self.dueno)
        url = reverse('curso_eliminar', args=[self.curso.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertTrue(Curso.objects.filter(pk=self.curso.pk).exists())
        self.assertEqual(self.client.post(url).status_code, 302)
        self.assertFalse(Curso.objects.filter(pk=self.curso.pk).exists())

    def test_csrf_en_mutaciones(self):
        cliente = Client(enforce_csrf_checks=True)
        cliente.force_login(self.dueno)
        self.assertEqual(cliente.post(reverse('curso_eliminar', args=[self.curso.pk])).status_code, 403)
        self.assertTrue(Curso.objects.filter(pk=self.curso.pk).exists())

    def test_mis_cursos_no_muestra_ajenos(self):
        self.otro.user_permissions.add(Permission.objects.get(content_type__app_label='portfolio', codename='add_curso'))
        self.client.force_login(self.otro)
        self.assertNotContains(self.client.get(reverse('mis_cursos')), self.curso.nombre)

    def test_validaciones_limites(self):
        for campo, valores in [('horas', [3, 201]), ('cupos', [4, 61])]:
            for valor in valores:
                form = CursoForm(self.datos_curso(**{campo: valor}))
                self.assertFalse(form.is_valid())
                self.assertIn(campo, form.errors)
        for horas, cupos in [(4, 5), (200, 60)]:
            self.assertTrue(CursoForm(self.datos_curso(horas=horas, cupos=cupos)).is_valid())

    def test_maximo_cinco_competencias(self):
        self.assertTrue(CursoForm(self.datos_curso(competencias=[e.pk for e in self.etiquetas[:5]])).is_valid())
        self.assertFalse(CursoForm(self.datos_curso(competencias=[e.pk for e in self.etiquetas])).is_valid())

    def test_area_opcional_y_set_null(self):
        self.assertTrue(CursoForm(self.datos_curso(area='')).is_valid())
        self.area.delete()
        self.curso.refresh_from_db()
        self.assertIsNone(self.curso.area)

    def test_busca_descripcion_y_pagina_con_filtro(self):
        for i in range(7):
            Curso.objects.create(nombre=f'Otro {i}', descripcion='Aprende fórmulas', horas=20, cupos=10,
                modalidad='online', fecha_inicio=self.curso.fecha_inicio, relator=self.dueno, area=self.area)
        respuesta = self.client.get(reverse('curso_lista'), {'q': 'fórmulas', 'area': self.area.pk})
        self.assertEqual(respuesta.context['page_obj'].paginator.count, 8)
        self.assertEqual(len(respuesta.context['page_obj']), 5)
        self.assertIn('area=', respuesta.context['querystring'])
        self.assertContains(respuesta, 'page=2')
        segunda = self.client.get(reverse('curso_lista'), {'q': 'fórmulas', 'area': self.area.pk, 'page': 2})
        self.assertEqual(len(segunda.context['page_obj']), 3)

    def test_parametros_invalidos_no_rompen(self):
        for params in [{'page': 'abc'}, {'page': 999}, {'area': 'abc'}, {'area': '9' * 100}, {'area': '²'}]:
            self.assertEqual(self.client.get(reverse('curso_lista'), params).status_code, 200)

    def test_n_mas_uno_resuelto(self):
        for i in range(5):
            Curso.objects.create(nombre=f'Otro {i}', descripcion='Otro', horas=20, cupos=10,
                modalidad='online', fecha_inicio=self.curso.fecha_inicio, relator=self.dueno, area=self.area)
        with self.assertNumQueries(2):
            for curso in cursos_relacionados():
                str(curso.area)
                str(curso.relator)
                list(curso.competencias.all())

    def test_correo_repetido_en_registro_y_perfil(self):
        form = RegistroForm({'username': 'nuevo', 'email': 'RELATOR@example.com',
                             'password1': 'ClaveNueva-482!', 'password2': 'ClaveNueva-482!'})
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        perfil = PerfilForm({'email': 'RELATOR@example.com'}, instance=self.otro)
        self.assertFalse(perfil.is_valid())
        self.assertTrue(PerfilForm({'email': self.dueno.email}, instance=self.dueno).is_valid())

    def test_registro_login_logout(self):
        respuesta = self.client.post(reverse('registro'), {'username': 'nuevo', 'email': 'nuevo@example.com',
            'password1': 'ClaveNueva-482!', 'password2': 'ClaveNueva-482!'}, follow=True)
        self.assertContains(respuesta, 'Tu cuenta está lista')
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)
        self.assertIn('_auth_user_id', self.client.session)
        self.client.post(reverse('logout'))
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(self.client.post(reverse('login'), {'username': 'nuevo', 'password': 'ClaveNueva-482!'}).status_code, 302)

    def test_cambio_clave_conserva_sesion(self):
        self.client.force_login(self.dueno)
        respuesta = self.client.post(reverse('cambiar_clave'), {'old_password': 'ClavePrueba-482!',
            'new_password1': 'OtraClave-8742!', 'new_password2': 'OtraClave-8742!'}, follow=True)
        self.assertContains(respuesta, 'Contraseña actualizada')
        self.assertIn('_auth_user_id', self.client.session)
        self.dueno.refresh_from_db()
        self.assertTrue(self.dueno.check_password('OtraClave-8742!'))

    def test_matricula_valida_y_duplicado(self):
        self.client.force_login(self.otro)
        url = reverse('matricular', args=[self.curso.pk])
        self.assertEqual(self.client.post(url, {'empresa': 'Empresa prueba', 'estado': 'confirmada'}).status_code, 302)
        matricula = Matricula.objects.get()
        self.assertEqual(matricula.estado, 'solicitada')
        self.assertEqual(self.client.post(url, {'empresa': 'Otra'}).status_code, 200)
        self.assertEqual(Matricula.objects.count(), 1)

    def test_duplicado_bloqueado_en_base_de_datos(self):
        Matricula.objects.create(curso=self.curso, participante=self.otro, empresa='Empresa')
        with self.assertRaises(IntegrityError), transaction.atomic():
            Matricula.objects.create(curso=self.curso, participante=self.otro, empresa='Otra')

    def test_matricula_propia_y_pasada(self):
        url = reverse('matricular', args=[self.curso.pk])
        self.client.force_login(self.dueno)
        self.assertContains(self.client.post(url, {'empresa': 'Empresa'}), 'propio curso')
        self.client.force_login(self.otro)
        self.curso.fecha_inicio = timezone.localdate() - timedelta(days=1)
        self.curso.save()
        self.assertContains(self.client.post(url, {'empresa': 'Empresa'}), 'ya comenzó')
        self.assertEqual(Matricula.objects.count(), 0)

    def test_matricula_hoy_permitida(self):
        self.curso.fecha_inicio = timezone.localdate()
        self.curso.save()
        matricula = Matricula(curso=self.curso, participante=self.otro, empresa='Empresa')
        matricula.full_clean()

    def test_cancelar_solo_propia_solicitada(self):
        matricula = Matricula.objects.create(curso=self.curso, participante=self.otro, empresa='Empresa')
        url = reverse('matricula_cancelar', args=[matricula.pk])
        self.client.force_login(self.tercero)
        self.assertEqual(self.client.post(url).status_code, 403)
        self.client.force_login(self.otro)
        self.assertEqual(self.client.get(url).status_code, 405)
        self.client.post(url)
        matricula.refresh_from_db()
        self.assertEqual(matricula.estado, 'anulada')
        matricula.estado = 'confirmada'
        matricula.save()
        respuesta = self.client.post(url, follow=True)
        self.assertContains(respuesta, 'Solo puedes cancelar')
        matricula.refresh_from_db()
        self.assertEqual(matricula.estado, 'confirmada')

    def test_solo_relator_cambia_estado(self):
        matricula = Matricula.objects.create(curso=self.curso, participante=self.otro, empresa='Empresa')
        url = reverse('matricula_estado', args=[matricula.pk])
        self.client.force_login(self.otro)
        self.assertEqual(self.client.post(url, {'estado': 'confirmada'}).status_code, 403)
        self.client.force_login(self.dueno)
        self.assertEqual(self.client.get(url).status_code, 405)
        for estado in ['confirmada', 'anulada']:
            self.client.post(url, {'estado': estado})
            matricula.refresh_from_db()
            self.assertEqual(matricula.estado, estado)
        self.client.post(url, {'estado': 'inventado'})
        matricula.refresh_from_db()
        self.assertEqual(matricula.estado, 'anulada')

    def test_listas_matriculas_aisladas(self):
        self.tercero.user_permissions.add(Permission.objects.get(content_type__app_label='portfolio', codename='add_curso'))
        Matricula.objects.create(curso=self.curso, participante=self.otro, empresa='Empresa privada')
        self.client.force_login(self.tercero)
        for nombre in ['mis_matriculas', 'matriculas_recibidas']:
            self.assertNotContains(self.client.get(reverse(nombre)), 'Empresa privada')

    def test_area_creada_desde_sitio(self):
        self.client.force_login(self.dueno)
        self.assertEqual(self.client.post(reverse('area_crear'), {'nombre': 'Gestión'}).status_code, 302)
        self.assertTrue(Area.objects.filter(nombre='Gestión').exists())

    def test_perfil_solo_usuario_actual(self):
        self.client.force_login(self.otro)
        self.client.post(reverse('perfil_editar'), {'email': 'nuevo@example.com', 'first_name': 'Nuevo', 'id': self.dueno.pk})
        self.dueno.refresh_from_db()
        self.otro.refresh_from_db()
        self.assertEqual(self.dueno.email, 'relator@example.com')
        self.assertEqual(self.otro.email, 'nuevo@example.com')

    def test_paginas_privadas_renderizan(self):
        self.client.force_login(self.dueno)
        for nombre in ['cuenta', 'perfil_editar', 'cambiar_clave', 'curso_crear', 'mis_cursos', 'area_crear']:
            self.assertEqual(self.client.get(reverse(nombre)).status_code, 200)

    def test_admin_permite_asignar_relator(self):
        admin = User.objects.create_superuser('admin', 'admin@example.com', 'ClavePrueba-482!')
        self.client.force_login(admin)
        url = reverse('admin:portfolio_curso_add')
        self.assertContains(self.client.get(url), 'name="relator"')
        datos = self.datos_curso(relator=self.dueno.pk, _save='Guardar')
        self.assertEqual(self.client.post(url, datos).status_code, 302)
        self.assertEqual(Curso.objects.get(nombre='Curso nuevo').relator, self.dueno)
        for modelo in ['area', 'competencia', 'curso', 'matricula']:
            self.assertEqual(self.client.get(reverse(f'admin:portfolio_{modelo}_changelist')).status_code, 200)

    def test_participante_no_publica_ni_entra_admin(self):
        self.client.force_login(self.otro)
        for nombre in ['curso_crear', 'area_crear', 'mis_cursos', 'matriculas_recibidas']:
            self.assertEqual(self.client.get(reverse(nombre)).status_code, 403)
            self.assertEqual(self.client.post(reverse(nombre), self.datos_curso()).status_code, 403)
        self.assertFalse(Curso.objects.filter(nombre='Curso nuevo').exists())
        self.assertEqual(self.client.get(reverse('admin:index')).status_code, 302)
        self.assertNotContains(self.client.get(reverse('curso_lista')), '+ Publicar curso')
        self.assertNotContains(self.client.get(reverse('cuenta')), 'Administración')
        self.assertRedirects(self.client.get(reverse('home')), reverse('cuenta'))

    def test_grupo_creador_y_admin_sin_cambiar_password(self):
        password = self.otro.password
        call_command('configurar_roles', creador=['alumno'], administrador=['relator'], stdout=StringIO())
        call_command('configurar_roles', creador=['alumno'], administrador=['relator'], stdout=StringIO())
        usuario = User.objects.get(pk=self.otro.pk)
        self.assertTrue(usuario.has_perm('portfolio.add_curso'))
        self.assertFalse(usuario.is_staff)
        self.assertEqual(usuario.password, password)
        administrador = User.objects.get(pk=self.dueno.pk)
        self.assertTrue(administrador.is_staff and administrador.is_superuser)
        self.client.force_login(usuario)
        self.assertEqual(self.client.get(reverse('curso_crear')).status_code, 200)

    def test_resumen_personal_aisla_datos_y_excluye_anuladas(self):
        Matricula.objects.create(curso=self.curso, participante=self.otro, empresa='Empresa', estado='anulada')
        Matricula.objects.create(curso=self.curso, participante=self.tercero, empresa='Otra', estado='solicitada')
        self.client.force_login(self.otro)
        respuesta = self.client.get(reverse('cuenta'))
        self.assertEqual(respuesta.context['total_cursos'], 0)
        self.assertEqual(respuesta.context['total_matriculas'], 1)
        self.assertEqual(respuesta.context['matriculas_activas'], 0)
        self.assertEqual(respuesta.context['pendientes_recibidas'], 0)
        self.assertEqual(list(respuesta.context['cursos_personales']), [])
        self.client.force_login(self.dueno)
        self.assertEqual(self.client.get(reverse('cuenta')).context['pendientes_recibidas'], 1)

    def test_matricula_transferida_no_se_puede_confirmar(self):
        matricula = Matricula.objects.create(curso=self.curso, participante=self.dueno, empresa='Historial', estado='anulada')
        self.client.force_login(self.dueno)
        self.client.post(reverse('matricula_estado', args=[matricula.pk]), {'estado': 'confirmada'})
        matricula.refresh_from_db()
        self.assertEqual(matricula.estado, 'anulada')

    def test_admin_tema_busqueda_filtros_y_eliminacion_area(self):
        administrador = User.objects.create_superuser('gestor', 'gestor@example.com', 'ClavePrueba-482!')
        self.client.force_login(administrador)
        self.assertContains(self.client.get(reverse('admin:index')), 'Cuida lo que')
        self.assertContains(self.client.get(reverse('admin:index')), 'admin-oniria.css')
        listado = reverse('admin:portfolio_curso_changelist')
        respuesta = self.client.get(listado, {'q': 'Excel', 'modalidad__exact': 'online'})
        self.assertEqual(list(respuesta.context['cl'].queryset), [self.curso])
        self.assertEqual(self.client.get(listado, {'q': 'inexistente'}).context['cl'].result_count, 0)
        datos = self.datos_curso(relator=self.dueno.pk, competencias=[e.pk for e in self.etiquetas], _save='Guardar')
        self.assertContains(self.client.post(reverse('admin:portfolio_curso_add'), datos), 'máximo de cinco')
        self.assertFalse(Curso.objects.filter(nombre='Curso nuevo').exists())
        url = reverse('admin:portfolio_area_delete', args=[self.area.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertTrue(Area.objects.filter(pk=self.area.pk).exists())
        self.assertEqual(self.client.post(url, {'post': 'yes'}).status_code, 302)
        self.curso.refresh_from_db()
        self.assertIsNone(self.curso.area)
        limitado = User.objects.create_user('staff_limitado', is_staff=True)
        limitado.user_permissions.add(Permission.objects.get(content_type__app_label='portfolio', codename='view_curso'))
        self.client.force_login(limitado)
        self.assertEqual(self.client.get(listado).status_code, 200)
        self.assertEqual(self.client.get(reverse('admin:portfolio_curso_add')).status_code, 403)

    def test_inicio_contadores_y_ultimos_cuatro(self):
        Matricula.objects.create(curso=self.curso, participante=self.otro, empresa='Empresa', estado='confirmada')
        for i in range(5):
            Curso.objects.create(nombre=f'Nuevo {i}', descripcion='Otro', horas=20, cupos=10,
                modalidad='online', fecha_inicio=self.curso.fecha_inicio, relator=self.dueno)
        respuesta = self.client.get(reverse('home'))
        self.assertEqual(len(respuesta.context['cursos']), 4)
        self.assertEqual(respuesta.context['cursos'][0].nombre, 'Nuevo 4')
        self.assertEqual(respuesta.context['total_cursos'], 6)
        self.assertEqual(respuesta.context['total_areas'], 1)
        self.assertEqual(respuesta.context['total_matriculas'], 1)

    def test_seed_demo_idempotente(self):
        call_command('seed_demo', stdout=StringIO())
        cuenta = User.objects.get(username='demo_relator')
        password = cuenta.password
        cursos = Curso.objects.count()
        call_command('seed_demo', stdout=StringIO())
        cuenta.refresh_from_db()
        self.assertEqual(cuenta.password, password)
        self.assertEqual(Curso.objects.count(), cursos)
        self.assertEqual(Matricula.objects.count(), 5)

    def test_login_erroneo_y_password_debil(self):
        respuesta = self.client.post(reverse('login'), {'username': 'relator', 'password': 'incorrecta'})
        self.assertEqual(respuesta.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
        form = RegistroForm({'username': 'debil', 'email': 'debil@example.com', 'password1': '123', 'password2': '123'})
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
