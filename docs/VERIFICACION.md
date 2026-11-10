# Verificación de la implementación

Última revisión: 10 de noviembre de 2026, hora de Santiago.

| Comprobación | Resultado |
| --- | --- |
| Base original | Commit c881eef25eab5ecaed2c583bce5c365930b0a6b2 del repositorio del profesor, historial conservado |
| Entorno | Python 3.14, Django 5.2.19, MySQL 8.0.46; dependencias en requirements-lock.txt |
| MySQL | Instancia local independiente; configuración y credenciales fuera de Git |
| Consistencia de modelos | `makemigrations --check --dry-run`: sin cambios pendientes |
| Configuración | `manage.py check --database default`: sin problemas |
| Pruebas rápidas | 42 pruebas aprobadas con `miempresa.settings_test` y SQLite en memoria |
| Pruebas de integración | 42 pruebas aprobadas con MySQL; `test_otec` se creó para la prueba y se eliminó al terminar |
| Relaciones | La prueba N+1 comprueba dos consultas para cursos y sus relaciones |
| Roles | Participante sin publicación; Creadores con permisos explícitos; administrador con acceso al admin |
| Datos de esta instalación | 10 cursos de Fer; participante user@fer.com sin cursos ni permisos administrativos |
| Admin | Cuatro entidades, búsqueda, filtros, permisos, alta con relator y máximo de cinco competencias verificados |
| Eliminación de área | Confirmación GET sin borrar; POST elimina área y conserva curso mediante SET_NULL, en base de prueba |
| Cuenta | Datos aislados por usuario; matrículas activas separadas del historial |
| Inspección visual | Cuenta, catálogo, matrículas y formulario admin revisados en escritorio y móvil de 390 px; sin desbordamiento horizontal de página en las vistas móviles comprobadas |
| Portada | Transición entre ilustración, contadores y carrusel revisada en escritorio |

La revisión visual conservó los datos reales del proyecto. Las pruebas de escritura se ejecutaron en bases aisladas. Se corrigieron recortes del encabezado y de los campos del admin móvil; las tablas anchas usan desplazamiento propio. Una comprobación adicional del participante en el navegador integrado se interrumpió por un error de conexión del navegador; los permisos y su vista quedaron comprobados mediante las pruebas automatizadas.

## Límites del alcance

La configuración predeterminada usa MySQL. SQLite se mantiene como alternativa explícita de pruebas/vista previa. Publicar el código en GitHub no despliega el sitio ni publica la base de datos. Las cuentas y contraseñas locales no se transfieren al clonar: deben crearse en cada instalación.

El cambio de roles es una ampliación solicitada y está explicado en EV3.md. La comprensión individual, la modificación en vivo y la trazabilidad de clases siguen siendo responsabilidad del estudiante. Estas comprobaciones no atribuyen una nota ni aprobación del docente.
