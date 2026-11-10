# Oniria con inspiración zakAi

Referencia consultada: DESIGN.md del proyecto local zakAi-Web y sus ilustraciones studio-desktop-v7.webp y studio-mobile-v6.webp. Se adopta la composición ilustrada con volumen, sombras de contacto, materiales oscuros y tipografía Space Grotesk. La corrección del usuario fija púrpura y amarillo en lugar de cian y salmón y solicita gráficos inspirados en Buda.

La escena principal es una ilustración original generada con la herramienta integrada image_gen. Archivo final: portfolio/static/images/oniria-sanctuary-v1.png. No se copiaron la escena del programador ni sus interacciones a la aplicación. El catálogo, las matrículas y el CRUD permanecen en Django. La tipografía local procede del proyecto zakAi-Web; se conserva su licencia OFL junto al archivo.

## Prompt utilizado

Use case: stylized-concept. Asset type: production hero artwork for Oniria, a lucid-dream course website. Wide landscape 1536x1024. Create a premium illustrated dimensional meditation sanctuary, with a respectful serene seated Buddha statue on a sculpted lotus pedestal occupying the RIGHT HALF, a large softly illuminated golden circular halo behind the head, purple stone architectural arch, layered lotus petals, a closed dream journal and small warm lantern on foreground steps. LEFT THIRD almost empty deep aubergine shadow, usable negative space. Art direction: detailed hand-painted 3D-like studio illustration, tangible bevels and material volume, fine clean contours, deep contact shadows, matte black and purple surfaces, selective rich golden YELLOW highlights, subtle purple rim light, restrained glow. Calm confident contemporary editorial art, not a photo, not cartoon emojis, not a flat vector, not generic neon space planets. Strong readable silhouette, beautiful cloth folds on statue, stylized carved facial features and closed eyes, respectful tranquil expression. Palette black-plum #100c18, royal purple #7149b5, warm yellow #f1cd53, pale ivory. Whole statue fits within frame, all feet lotus and halo intact, generous space above. No text, no letters, no logos, no watermarks. Website artwork only, not a screenshot or UI mockup.

## Integración del fondo

La portada usa la clase `home-page` para colocar la navegación transparente sobre la misma escena. La ilustración conserva su archivo original y utiliza máscaras CSS horizontales y verticales para disolver sus bordes contra el fondo púrpura. En móvil, la imagen mantiene un encuadre vertical bajo el texto, sin invadir la navegación. El enlace Crear cuenta usa un contorno amarillo discreto en la portada.

Verificación: `manage.py check` sin incidencias; revisión visual de escritorio y móvil de 390 px, incluida la unión con el catálogo y la ausencia de desbordamiento horizontal en móvil.

Los accesos principales usan texto dorado subrayado y una flecha en un aro doble que recoge la forma del halo. El aro responde a hover y foco; respeta movimiento reducido. Verificados en escritorio y móvil y comprobado el enlace al catálogo.

## Composición móvil revisada

La composición móvil reemplaza el bloque largo de texto seguido de imagen por una portada centrada: título, ilustración, descripción y acceso a cursos. Los tres contadores cierran la portada. Se ocultan sólo el pie decorativo de la escena y el enlace secundario redundante.

La cabecera móvil muestra marca y Menú. El desplegable conserva todos los enlaces de la sesión, admite Escape con retorno del foco, clic exterior y reinicio al cambiar de breakpoint. Sin JavaScript, los enlaces siguen visibles. El escritorio conserva su navegación abierta.

Verificación: vista a 390 y 320 px, sin desbordamiento horizontal a 320 px; apertura/cierre por teclado del menú; comprobación de escritorio a 1440 px; `manage.py check` sin incidencias.

## Catálogo y detalles ilustrados

El catálogo presenta los resultados filtrados en un carrusel horizontal con símbolos de ojo, constelación, órbitas, fases, loto y bitácora. Conserva búsqueda, filtro de área y paginación de cinco registros. El carrusel ofrece desplazamiento táctil, botones, teclado y movimiento reducido; no tiene reproducción automática.

Cada detalle muestra una cabecera ilustrada, datos de matrícula, y un carrusel de otros cursos que excluye el actual. Los seis temas nuevos incluyen recorrido y enlaces a fuentes. El contenido editorial demo se limita a cursos de los relatores demo; no añade un temario a cursos creados por otros usuarios.

Se sustituyeron seis cursos mediante `actualizar_temario_oniria`, conservando IDs, fechas, cupos y matrículas. La segunda ejecución no cambia datos. Respaldo previo local: `.local/temario-antes-noviembre.json`. Las 34 pruebas con `miempresa.settings_test` pasaron; se verificaron búsqueda y desplazamiento del carrusel en móvil sin desbordamiento horizontal.

Comprobación final: catálogo y detalle en escritorio, incluido el carrusel de cursos relacionados (avance de 01/06 a 02/06). La página no desborda horizontalmente en móvil ni escritorio. Capturas locales: `.local/oniria-catalogue-carousel.jpg` y `.local/oniria-course-detail.jpg`.

La portada reutiliza el carrusel ilustrado para sus cuatro cursos recientes. Cada tarjeta reúne gráfica, título, descripción, competencias y acceso al detalle en una superficie púrpura. Verificados cuatro cursos y cuatro SVG, avance con botones, teclado y móvil a 390 px sin desbordamiento de página. Pasaron las pruebas de portada/contadores y renderizado público (2 pruebas).

## Carrusel continuo, relieve y acceso emergente

`experience.css` añade marcos púrpura, medallones con relieve, sombras de contacto y una respuesta de perspectiva moderada al puntero. `carousel.js` conserva el conjunto real y añade copias visuales a ambos lados. Al terminar el desplazamiento se recentra en una posición equivalente; el contador usa el índice del curso original. Las copias no participan en el recorrido por teclado ni en el árbol accesible. El carrusel no avanza automáticamente. Admite desplazamiento nativo, arrastre con ratón, botones y teclado; respeta movimiento reducido.

El acceso usa un `dialog` nativo con ingreso y registro. Solicita formularios renderizados por Django y envía sus tokens CSRF. Los errores se muestran dentro de la ventana; el éxito devuelve el destino en JSON para no consumir los mensajes flash mediante una navegación previa invisible. Las rutas completas siguen funcionando sin JavaScript. Se conserva `next` y se rechazan destinos externos al registrarse. Escape cierra y devuelve el foco; en móvil los formularios largos se desplazan dentro de la ventana.

Verificación visual: vuelta del primero al último y arrastre del último al primero en móvil; cuatro tarjetas originales; página sin desbordamiento horizontal a 390 px. Login real con error y después éxito; formulario de registro móvil hasta el botón final y cierre con Escape. No se efectuó un registro de prueba en la base real.

## Propiedad y cuentas locales

Los 10 cursos existentes se asignaron a `fer@fer.com`. Sus gráficas y contenidos se conservan. Se creó `user@fer.com` como usuario activo normal, sin staff, superusuario, grupos ni permisos específicos y sin cursos propios. La aplicación mantiene su modelo original: las cuentas normales pueden actuar como participantes y relatores.

La matrícula pendiente 6 de Fer para el curso 9 pasó a anulada al convertirse Fer en relator; se conserva como historial. `seed_demo` reutiliza al propietario Fer si existe, para evitar duplicar el catálogo después de esta transferencia.

## Mi espacio, administración y continuidad (10 noviembre)

Se reemplazó la cuenta de dos paneles por una bienvenida ilustrada, indicadores enlazados, cursos recientes y un perfil secundario. El participante recibe una vista orientada al aprendizaje y el creador accesos de gestión. La ilustración usa el recurso aprobado, sin cambiarlo. En móvil el perfil se ordena debajo de la actividad.

La portada integra contadores y carrusel con menos separaciones y espacio vertical. El catálogo reduce la portada, conserva el Buda completo en escritorio y da prioridad a búsqueda, filtros y cursos. Se mantienen cuatro cursos de portada, cinco por página en catálogo y desplazamiento circular. Mis cursos usa filas ilustradas; matrículas conserva tabla semántica en escritorio y se reorganiza en fichas en móvil. Los estados tienen texto además de color.

El admin incorpora tipografía local, púrpura/amarillo, cabecera propia, tema claro alternativo, listas, formularios y estado de foco. Conserva plantillas nativas mediante herencia, sin dependencias nuevas. Se corrigieron el ancho de la barra lateral, el encogimiento flex del header móvil y el ancho nativo de los contenedores de formulario, para evitar recortes. Las tablas administrativas anchas se desplazan en su propio contenedor.

La regla vigente de roles reemplaza la descripción anterior de publicación para cualquier cuenta: los participantes no publican; Creadores concede permisos explícitos; Fer es administrador. El admin permite asignar ese grupo.
