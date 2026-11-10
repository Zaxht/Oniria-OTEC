# OTEC Capacitación

Identidad visual actual: **Oniria · Escuela de sueños**. El catálogo de demostración contiene diez cursos sobre sueños lúcidos, registro de sueños y creatividad onírica, con tres áreas y cinco competencias. Los contenidos se definen en `portfolio/demo_catalogo.py`; `seed_demo` utiliza esta temática para instalaciones nuevas. El comando `adaptar_suenos_lucidos` convierte los cursos demo originales sin cambiar sus IDs ni sus matrículas.

Aplicación Django para publicar cursos y gestionar matrículas, adaptada del proyecto del profesor Franco Morales para el Caso 06 y la Evaluación Sumativa 3 de TI3041.

## Base y alcance

Origen: https://github.com/francolmc/Backend2026.Miempresa-UnaCositaDulce

Commit base: `c881eef25eab5ecaed2c583bce5c365930b0a6b2`.

Se conservaron `manage.py`, el proyecto `miempresa`, la aplicación `portfolio`, las vistas por funciones y la herencia de `portfolio_base.html`. La clase Python con datos estáticos se reemplazó por modelos persistentes. Las páginas de ejemplo se adaptaron a la navegación del organismo de capacitación.

## Instalar y ejecutar en Windows

Si el proyecto ya esta instalado en este equipo, haz doble clic en **iniciar.bat** en la carpeta OTEC. Usa directamente Python de `.venv`, inicia MySQL si hace falta y ejecuta Django; no requiere activar el entorno ni ejecutar archivos PowerShell. Manten la ventana abierta y visita http://127.0.0.1:8000/. Ctrl+C detiene Django.

Desde una terminal en la carpeta del proyecto tambien puedes ejecutar `.\iniciar.bat`. Para comprobar solo la conexion: `.\iniciar.bat --check`.

Requiere Python 3.12 o posterior y MySQL 8.0.11 o posterior. Dependencias probadas en `requirements-lock.txt`.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
```

Hay dos opciones para MySQL. Elige una.

### Instancia OTEC independiente

Si MySQL está instalado en la ruta habitual, este comando crea una instancia nueva en `127.0.0.1:3307`, sin modificar servicios existentes. Genera `.env`, la base `otec`, un usuario limitado a `otec` y `test_otec`, y contraseñas aleatorias. Rechaza sobrescribir configuración o datos existentes.

```powershell
.\.venv\Scripts\python.exe scripts\bootstrap_mysql.py
```

Los datos y credenciales administrativas de esta instancia quedan en `.local/`, fuera de Git. La base se conserva al cerrar el proceso. Para reiniciar la instancia después de reiniciar Windows:

```powershell
.\scripts\iniciar_mysql.ps1
```

El parámetro `--mysqld` del script Python permite indicar otra ruta al ejecutable.

### Servidor MySQL propio

Crea una base `otec` con `utf8mb4` y un usuario con permisos sobre ella. Copia `.env.example` a `.env` y completa DB_NAME, DB_USER, DB_PASSWORD, DB_HOST y DB_PORT. Para ejecutar pruebas en ese servidor, el usuario necesita crear y eliminar la base exclusiva `test_otec`. No uses una base de producción como base de pruebas.

### Migraciones, datos y servidor

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Abre http://127.0.0.1:8000/ y el panel administrativo en http://127.0.0.1:8000/admin/.

`seed_demo` crea tres cuentas ficticias: `demo_relator`, `demo_participante` y `demo_relatora`. La contraseña se toma de OTEC_DEMO_PASSWORD en `.env`, si está definido; de lo contrario genera una y la informa. Solo muestra la contraseña al crear cuentas nuevas. Repetir el comando no sobrescribe contraseñas ni cambios a cursos existentes.

Los datos de ejemplo son 10 cursos futuros, 3 áreas, 5 competencias y 5 matrículas en distintos estados. No representan estudiantes ni empresas reales. Las cuentas demo no tienen acceso al administrador.

## Verificación

```powershell
# Verificación real con MySQL (configuración predeterminada)
.\.venv\Scripts\python.exe manage.py check --database default
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py medir_consultas
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run

# Pruebas rápidas aisladas sin requerir MySQL
.\.venv\Scripts\python.exe manage.py test --settings=miempresa.settings_test
```

Existe también `miempresa.settings_demo`, que usa un archivo SQLite para una vista previa explícita sin MySQL. No es la configuración de entrega ni sustituye el requisito de MySQL. Las pruebas rápidas usan una base temporal; el servidor normal siempre usa MySQL.

## Organización

| Archivo | Responsabilidad |
| --- | --- |
| `portfolio/models.py` | Relaciones, rangos y validaciones de matrícula |
| `portfolio/forms.py` | Formularios, correo no repetido y máximo de cinco competencias |
| `portfolio/views.py` | Consultas, permisos, CRUD, perfil y matrículas |
| `miempresa/urls.py` | Rutas públicas y protegidas |
| `portfolio/admin.py` | Administración de las cuatro entidades |
| `portfolio/templates/` | Plantilla base y pantallas de usuario |
| `portfolio/tests.py` | Casos normales, límites y permisos |
| `docs/EV3.md` | Matriz de requisitos, decisiones y guía de defensa |
| `docs/AVANCE.md` | Avance de implementación y registro para sesiones futuras |
| [docs/USO_IA.docx](docs/USO_IA.docx) | Tres ejemplos simulados de consultas específicas a la IA y su validación |

## Decisiones del negocio

- Una misma cuenta puede actuar como relator y participante de cursos ajenos. No se añaden roles excluyentes.
- Eliminar un área conserva los cursos mediante SET_NULL. Eliminar un curso elimina sus matrículas con confirmación previa. Eliminar un usuario desde administración elimina sus cursos y matrículas; es una operación administrativa, no una función del perfil.
- Una matrícula anulada conserva el historial y bloquea otra solicitud del mismo usuario al mismo curso. El relator puede confirmar o anular matrículas recibidas, incluida una anulada; el caso no define estados terminales.
- El día de inicio todavía admite solicitudes; se bloquean fechas anteriores al día actual en America/Santiago.
- Los cupos se validan entre 5 y 60. El caso no exige control de ocupación ni lista de espera, por lo que no se inventa esa regla.
- La validación de correo único se aplica en registro y perfil, ignorando mayúsculas; se conserva `User` de Django. Su campo email no tiene restricción única nativa, por lo que inserciones externas o concurrentes podrían requerir un modelo de usuario personalizado si el alcance evoluciona.
- Las imágenes son una ampliación opcional de la cápsula 11 y no forman parte de los quince requisitos implementados.

Esta configuración es para desarrollo y demostración académica local. No se ha publicado en Internet.

## Temario de sueños lúcidos

Seis cursos demo cubren definición e historia, ciencia, métodos, fases, riesgos y cuidados, y consejos desde relatos reales publicados. Los cuatro restantes mantienen la línea creativa. Para actualizar una instalación con los títulos anteriores: `python manage.py actualizar_temario_oniria`. Conserva matrículas y no modifica cursos de otros autores.

Las fuentes están enlazadas en cada detalle: LaBerge et al. (1981), Konkoly et al. (2021), estudio internacional de inducción (2020), NIH sobre fases del sueño, y Sleep Advances (2022) sobre experiencias publicadas. Los testimonios se distinguen de evidencia de eficacia; el curso de fases no presenta la lucidez como una secuencia clínica obligatoria.

## Roles de Oniria

Los registros nuevos son participantes. Para habilitar publicación a una cuenta existente, asígnala al grupo **Creadores** desde Admin → Usuarios, o ejecuta:

```powershell
.\.venv\Scripts\python.exe manage.py configurar_roles --creador nombre_usuario
```

Los relatores demo reciben ese grupo al crearse; repetir seed_demo no restaura roles revocados. La sesión iniciada dirige la portada a Mi espacio. En esta instalación `fer@fer.com` es administrador y dueño de los diez cursos; `user@fer.com` es participante. Las contraseñas no cambiaron.
