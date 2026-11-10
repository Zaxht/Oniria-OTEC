# Declaración de asistencia de IA

Esta adaptación se desarrolló con asistencia de Codex sobre el repositorio original del profesor Franco Morales. La IA implementó modelos, formularios, vistas, rutas, plantillas, estilos, datos ficticios, comandos de configuración, pruebas y documentación a partir del caso 06, las cápsulas y la rúbrica compartidos por el estudiante.

No debe presentarse esta declaración como prueba de que el estudiante comprende todo el código. Antes de la defensa, el estudiante debe ejecutar la aplicación, revisar cada archivo y practicar modificaciones sin asistencia.

## Qué se verificó durante la implementación

- Restricciones de propiedad mediante acceso directo por URL y envíos POST.
- Rangos de horas y cupos, máximo de competencias y correo repetido.
- Guardado de competencias en creación y edición.
- Rechazo de matrículas propias, repetidas y con fecha pasada.
- Cancelación restringida al participante y a solicitudes pendientes; cambios de estado restringidos al relator.
- Conservación de filtros al paginar, entradas inválidas y optimización de consultas.
- Sesiones, logout por POST, CSRF, perfil y cambio de contraseña.

Los resultados ejecutados se registran en `VERIFICACION.md` al finalizar la revisión.

## Correcciones concretas a lo generado

La primera configuración de administración reutilizaba el formulario público de cursos, que excluye al relator. Se agregó `CursoAdminForm` con todos los campos para permitir que el administrador seleccione un relator sin exponer ese campo en el sitio público. La restricción de cinco competencias se conserva en ambos formularios.

Al integrar las cápsulas se mantuvo `save_m2m()` después de asignar al dueño. El ejemplo de subida de archivos no incluye esa llamada, pero el caso OTEC sí necesita persistir competencias al usar `commit=False`.

## Completar después de la revisión personal

- Archivos que puedo explicar sin asistencia: pendiente.
- Cambio que implementé personalmente: pendiente.
- Caso de error que probé y resultado: pendiente.
- Corrección que realicé personalmente a una sugerencia de IA: pendiente.

No reemplazar estos pendientes por afirmaciones que todavía no se hayan comprobado.
