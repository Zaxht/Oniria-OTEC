# Preparación de EV3 para el caso OTEC

La aplicación cubre los quince requisitos del caso. La defensa debe hacerse sobre este código, ejecutándolo y explicando cada decisión. Tener código asistido por IA no demuestra por sí solo comprensión ni participación en clases.

## Matriz de cumplimiento

| N.º | Requisito del caso | Implementación y comprobación | Rúbrica |
| --- | --- | --- | --- |
| 1 | MySQL propio | `miempresa/settings.py`, base `otec`; `check --database default` y pruebas con MySQL | A1 |
| 2 | Cuatro entidades y relaciones | `Area`, `Competencia`, `Curso`, `Matricula`; FK a User y M2M Curso–Competencia; migración inicial | A1 |
| 3 | Administración | `admin.py`: list_display, list_filter, search_fields en las cuatro entidades | Requisito del caso |
| 4 | Portada | Cuatro cursos recientes; contadores de cursos, áreas y matrículas confirmadas | Caso, A9 |
| 5 | Listado | Q por nombre y descripción, área, cinco por página, orden estable y relaciones precargadas | A6, A7 |
| 6 | Detalle | Datos propios, área, competencias y relator | A3, A7 |
| 7 | Registro y sesiones | UserCreationForm, email__iexact, LoginView, LogoutView con POST y CSRF | A4 |
| 8 | Mi cuenta | Ver datos, editar perfil y PasswordChangeView manteniendo sesión | A8 |
| 9 | CRUD propio | CursoForm, precarga, confirmación, mensajes y rangos | A2, A3, A9 |
| 10 | Dueño y mis registros | request.user, comprobar_dueno, 403 en GET y POST, Mis cursos | A5 |
| 11 | Catálogo y etiquetas | Área opcional, competencias con máximo cinco, save_m2m, creación de áreas | A2, A7 |
| 12 | Eliminación del catálogo | SET_NULL; comprobación automatizada de conservación del curso | A1, B4 |
| 13 | Solicitudes ajenas | Matrícula valida dueño, fecha y duplicado; UniqueConstraint en base de datos | Caso, A5, B4 |
| 14 | Mis solicitudes | Lista filtrada por participante y cancelación solo solicitada | Caso, B2 |
| 15 | Solicitudes recibidas | Lista filtrada por relator; cambio POST a confirmada/anulada | Caso, B4 |

El Caso 06 exige como datos de prueba mínimos: 3 usuarios, **10 cursos**, 3 áreas, 5 competencias y 5 matrículas en distintos estados. La portada muestra los **4 cursos más recientes**, no todo el catálogo. La rúbrica evalúa las funcionalidades; la cantidad de datos proviene del documento del caso.

Los datos mínimos se cargan con `seed_demo`. El comando es idempotente y preserva ediciones posteriores.

## Cápsulas utilizadas

| Cápsula | Aplicación concreta |
| --- | --- |
| 01 Logout seguro | Formulario POST con csrf_token en portfolio_base.html |
| 02 Mensajes flash | Bloque común de messages; resultados del CRUD, perfil y matrículas |
| 03 Autenticación y autorización | login_required y comprobación de propiedad en las vistas |
| 04 on_delete | SET_NULL en área; CASCADE en dependencias cuya vida depende del registro |
| 05 Búsqueda y paginación | Q con OR, orden estable, Paginator.get_page y querystring conservado |
| 06 N+1 | select_related(area, relator), prefetch_related(competencias), medir_consultas |
| 07 Muchos a muchos | Guardar objeto y luego save_m2m al asignar el relator |
| 09 Mi cuenta | ModelForm sobre el usuario actual y PasswordChangeView |
| 10 Probar tu hito | Pruebas de permisos, rangos, error, sesiones y relaciones |
| 11 Archivos | Revisada; ampliación opcional no incluida en el alcance obligatorio |

## Recorrido de demostración

1. Sin sesión: abrir inicio, ver cuatro cursos y contadores; buscar una palabra presente solo en la descripción; filtrar y cambiar de página.
2. Registrarse con un correo nuevo. Intentar un correo ya usado, una clave débil y una clave de ingreso incorrecta.
3. Publicar un curso con área y dos competencias. Intentar 3 horas, 61 cupos y seis competencias; mostrar errores. Comprobar límites válidos 4/200 horas y 5/60 cupos.
4. Editar el curso: los campos y competencias deben estar precargados. Guardar otro conjunto de competencias.
5. Copiar URL de edición/eliminación. Ingresar con otro usuario y abrirla: 403. Sin sesión: redirección a ingresar. Un ID inexistente: 404.
6. Desde otra cuenta, solicitar matrícula. Repetir la solicitud y probar un curso propio o con fecha pasada: rechazo.
7. En Mis matrículas, cancelar una solicitada. En Recibidas, como dueño, confirmar o anular. Una matrícula confirmada no puede cancelarla el participante.
8. Editar el perfil sin cambiar el correo; luego intentar uno de otra persona. Cambiar contraseña y comprobar que la sesión sigue abierta.
9. Abrir confirmación de eliminación y volver sin borrar; luego confirmar con POST. Mostrar el mensaje y la desaparición del registro.
10. Ejecutar `medir_consultas`; explicar por qué diez cursos no generan consultas adicionales por cada relación.
11. En administración, eliminar un área y comprobar que sus cursos siguen existiendo sin área.

## Preguntas de defensa

- ¿Qué diferencia hay entre GET y POST? GET muestra el formulario; POST valida y modifica. CSRF protege los formularios frente a solicitudes cruzadas.
- ¿Por qué `login_required` no basta? Identifica al usuario, pero no prueba que el curso sea suyo. `comprobar_dueno` verifica autorización y devuelve 403.
- ¿Por qué `commit=False`? Permite asignar al dueño desde la sesión antes de guardar. Después `save_m2m` guarda la tabla intermedia usando el ID generado.
- ¿Qué hace `instance=curso`? Precarga y actualiza el registro existente en vez de crear uno nuevo.
- ¿Por qué el catálogo es SET_NULL? El curso puede existir sin área. Por eso null=True y blank=True permiten esa ausencia en la base y el formulario.
- ¿Cómo se evita un duplicado? Se verifica antes de guardar y una restricción única en MySQL evita dos escrituras del mismo curso y participante.
- ¿Por qué ordenar antes de paginar? Un orden determinista, con PK como desempate, evita resultados ambiguos entre páginas.
- ¿Qué optimiza select_related? Las relaciones FK se traen en JOIN; prefetch_related trae el conjunto M2M en una consulta adicional.
- ¿Dónde se guarda la contraseña? Django guarda un hash y PasswordChangeView valida la contraseña actual, la nueva y conserva la sesión actual.
- ¿Por qué no confiar en los campos ocultos? El cliente puede manipularlos; dueño, participante y estados permitidos se determinan en el servidor.

## Ejercicios para practicar sin ayuda

1. Agregar un filtro de modalidad y conservarlo al paginar. Probar un valor válido, uno inválido y la página 2.
2. Agregar un campo ubicación opcional al curso: modelo, migración, formulario y detalle.
3. Cambiar un límite de validación y actualizar la restricción y las pruebas. Explicar por qué no basta con HTML.

## Ponderación y diferencias entre documentos

La rúbrica detallada distribuye 50% proyecto, 35% defensa y 15% uso de IA. El caso describe 50/50 para práctico y preguntas. Además, el caso enumera cinco hitos y la rúbrica menciona cuatro. Consultar al docente esta diferencia; se implementaron los cinco hitos y se tomó la rúbrica detallada como guía de cobertura, sin atribuir una nota ni resolver por cuenta propia la contradicción.

## Roles y navegación (actualización solicitada)

La portada `/` es pública para visitantes. Una sesión autenticada redirige a `/cuenta/`, que conserva edición del perfil y cambio de contraseña (A8). La marca sigue esa misma regla.

Las cuentas nuevas son participantes. La publicación se protege con `permission_required('portfolio.add_curso', raise_exception=True)` además de `login_required`; crear áreas requiere `portfolio.add_area`. El grupo **Creadores** contiene esos permisos. Un creador no es staff ni recibe acceso al admin por pertenecer al grupo. Los controles públicos consultan los mismos permisos mediante `perms`; la propiedad de cada curso sigue verificándose en el servidor. Para demostrar A2/A3/A5, usar dos creadores y un participante; el registro por sí solo ya no concede publicación. Esta separación es una ampliación solicitada del flujo original del caso, no una exigencia nueva atribuida a la rúbrica.

`fer@fer.com` es administrador activo (`is_staff` y `is_superuser`) y conserva los 10 cursos y su contraseña. `user@fer.com` continúa como participante sin privilegios. Desde Admin → Usuarios se asigna el grupo Creadores; para la instalación local también existe `manage.py configurar_roles --creador nombre_usuario`. `--administrador nombre_usuario` concede administración completa y debe usarse solamente con el destinatario autorizado. El comando sin opciones crea el grupo sin elevar usuarios.

El admin usa el sistema nativo de Django: cuatro entidades registradas, `list_display`, `list_filter`, `search_fields`, formularios, permisos por modelo, CSRF, confirmación de eliminación e historial. El tema se limita a plantillas y CSS; los filtros y validaciones siguen operativos. Se probó crear un curso con relator, rechazar más de cinco competencias, buscar/filtrar, negar altas a staff con permiso solo de lectura y eliminar un área conservando el curso (`SET_NULL`). Las operaciones de escritura de prueba se hicieron en una base aislada.

La cuenta muestra matrículas activas (solicitadas + confirmadas) y conserva el total histórico aparte. Una matrícula anterior a una transferencia de propiedad no puede confirmarse si el participante ahora es el relator. No se eliminó ese historial.
