# Manual: gestionar las sesiones del Speaker's Corner en Nextcloud

Este manual explica cómo dar de alta, modificar y cancelar sesiones del Speaker's
Corner (charlas normales y eventos especiales como la Inauguración) desde
Nextcloud. **No hace falta tocar nada de GitHub ni de código** — todo se hace
desde el Calendario y desde Formularios, como cualquier otro documento de
Nextcloud.

La web (`https://speakers.cavecavet.org`) se actualiza sola cada 4 horas leyendo
el calendario. Si necesitas que se actualice al momento, pide a Juan que fuerce
la sincronización manualmente (tarda menos de un minuto).

## 1. El calendario que hay que usar

Calendario **"Xerrades Hotel Termes Montbrió"**, dentro de Nextcloud → Calendario.
Solo los eventos de este calendario aparecen en la web.

## 2. Dar de alta una charla normal (un ponente, un tema)

1. Crea un evento nuevo en el calendario, con la fecha y hora reales de la
   charla.
2. En **Ubicación**, escribe el lugar (ej. `Hotel Termes de Montbrió`).
3. En **Descripción**, escribe **exactamente** estas dos líneas, en este orden
   (la web busca este texto literal para saber quién es el ponente y cuál es el
   tema — si no sigues este formato, la web mostrará toda la descripción como
   título y no sabrá quién es el ponente):
   ```
   Ponent: Nombre del ponente
   Tema: Título de la charla
   ```
   Ejemplo real ya publicado:
   ```
   Ponent: Mercè Milán
   Tema: Beneficis de l'aigua i del mar per a la salut i el sistema nerviós. Recepta blava i Blue Mind.
   ```
4. **Marca el evento como "Confirmado"** (no lo dejes en "Tentativo"). Este es
   el paso más importante: la web **solo muestra sesiones confirmadas** — un
   evento tentativo/provisional es invisible en la web hasta que lo confirmes.
5. Guarda. En un máximo de 4 horas (o antes, si Juan fuerza la sincronización):
   - la sesión aparecerá en `speakers.cavecavet.org`,
   - se creará automáticamente un formulario de inscripción para esa sesión en
     Nextcloud Forms, con capacidad para 140 personas y que se cierra solo a la
     hora de inicio de la charla,
   - el formulario se compartirá automáticamente con el grupo **`admins`** de
     Nextcloud (tú ya estás dentro), para que puedas ver quién se ha apuntado
     sin ser tú quien lo creó.

**No hace falta que crees el formulario a mano** — se genera solo. Tampoco hace
falta que lo compartas contigo misma, el sistema ya lo hace.

## 3. Un evento especial con varios ponentes o actividades (ej. la Inauguración)

Si el evento no tiene un único ponente/tema (por ejemplo, una inauguración con
varias actividades y varias personas hablando), simplemente **no uses** el
formato `Ponent:`/`Tema:` de arriba. Escribe la descripción libremente, por
ejemplo:

```
Inauguración del Speaker's Corner Termes Montbrió.

19:00 — Bienvenida institucional (Ajuntament de Montbrió, Hotel Termes Montbrió)
19:15 — "El bienestar como proyecto de vida" — Mercè Milán
19:45 — "Filosofía de sobremesa" — Dr. Adrià Puig
20:30 — Cóctel y networking
```

La web mostrará todo este texto como título de la tarjeta (no destacará un
único ponente, ya que hay varios) y generará **un único formulario de
inscripción para todo el evento** — la gente se apunta una sola vez para
asistir a la inauguración completa, no charla por charla. Sigue funcionando el
límite de 140 plazas y el cierre a la hora de inicio, igual que con una charla
normal. Recuerda igualmente marcarlo como **Confirmado**.

Si quieres que este tipo de evento tenga una tarjeta más cuidada en la web
(por ejemplo, destacando los nombres de los ponentes por separado), coméntaselo
a Juan — hoy funciona, pero con el formato de texto libre tal cual lo escribas.

## 4. Cambiar la fecha o la hora de una sesión ya confirmada

Simplemente edita el evento en el calendario y cambia la fecha/hora. En la
siguiente sincronización (máx. 4h):

- la tarjeta de la web se actualiza sola a la fecha nueva,
- el formulario de Nextcloud Forms de esa sesión se actualiza solo (título,
  descripción y fecha de cierre),
- **si alguien ya se había inscrito, recibirá automáticamente un correo**
  avisando del cambio de fecha. Su inscripción se mantiene, no hace falta que
  vuelva a apuntarse.

No tienes que hacer nada más — ni avisar tú a mano, ni tocar el formulario.

## 5. Cancelar una sesión

Borra el evento del calendario, o cámbialo de "Confirmado" a "Tentativo"/otro
estado. En la siguiente sincronización:

- la sesión desaparece de la web,
- su formulario de Nextcloud Forms se **cierra** (deja de aceptar
  inscripciones nuevas, pero no se borra — el listado de quien ya se había
  apuntado se conserva),
- **las personas ya inscritas reciben un correo avisando de la cancelación.**

Una sesión que simplemente ya ha pasado (la fecha ya llegó) no cuenta como
cancelada — desaparece sola de la web sin ningún aviso, es lo normal.

## 6. Ver quién se ha inscrito

1. En Nextcloud, ve a **Formularios**.
2. Busca el formulario de la sesión que te interese (el título sigue el
   patrón `Confirmar asistencia — Speaker's Corner · <ponente o evento>`).
3. Ábrelo y entra en la pestaña **"Respuestas"**.
4. Ahí puedes ver todas las inscripciones, y también **descargarlas** en
   Excel/CSV/ODS con el botón de descarga, si necesitas la lista para otra
   cosa (imprimir, pasar lista el día del evento, etc.).

Como formas parte del grupo `admins`, puedes ver las respuestas de **todos**
los formularios de sesiones, no solo de los que crees tú misma.

## 7. Lo que el sistema NO hace todavía

- No corrige sola una sesión si cambias el **ponente** o el **lugar** sin
  cambiar la fecha (el formulario mantiene esos datos hasta la próxima vez que
  cambie la fecha). Si necesitas corregirlo ya, pide a Juan que lo actualice a
  mano, o simplemente cambia también la hora un minuto y vuelve a ponerla
  correcta para forzar la actualización.
- No envía recordatorios automáticos a los inscritos antes de la charla (solo
  avisa de cambios de fecha o cancelaciones).
- El formulario de "Quiero ser speaker" (para quien quiere proponer una
  charla) es fijo, no se genera uno nuevo por persona — es siempre el mismo
  formulario general.

## Resumen rápido

| Quiero... | Qué hago |
|---|---|
| Publicar una charla normal | Crear evento, `Ponent:`/`Tema:` en la descripción, marcar Confirmado |
| Publicar un evento con varios ponentes (Inauguración) | Crear evento, descripción libre, marcar Confirmado |
| Cambiar la fecha | Editar la fecha del evento — el resto es automático (formulario + aviso por email) |
| Cancelar | Borrar el evento o quitarle el Confirmado — el resto es automático (cierre + aviso por email) |
| Ver inscritos | Formularios → el formulario de esa sesión → pestaña Respuestas |
