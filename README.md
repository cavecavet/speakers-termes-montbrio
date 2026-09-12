# Speaker's Corner Termes Montbrió

Lloc estàtic (sense build) del cicle de xerrades organitzat per l'Associació Cave
Cavet i l'Hotel Termes Montbrió. Publicat a **https://speakers.cavecavet.org/** via
GitHub Pages.

- Disseny i decisions: `docs/superpowers/specs/2026-09-11-speakers-termes-montbrio-design.md`
- L'agenda (`data/agenda.json`) es genera automàticament — **no s'edita a mà**. La
  font és el calendari Nextcloud `Xerrades Hotel Termes Montbrió`
  (`https://cloud.cavecavet.org/apps/calendar/p/RP5xH59a33ZBNwLx`).

## Com afegir una sessió al lloc

Al calendari Nextcloud, per a cada xerrada:

1. Crea l'esdeveniment amb la data i l'hora reals.
2. **Marca'l com a Confirmat** (no «Tentatiu»/«provisional») — el lloc **només**
   mostra esdeveniments confirmats; els provisionals queden invisibles fins que
   els confirmis.
3. A la descripció, escriu-hi exactament aquest format (dues línies, en aquest
   ordre — el sincronitzador el busca literalment):
   ```
   Ponent: <nom del ponent>
   Tema: <títol de la xerrada>
   ```
   Si no segueixes aquest format, el lloc mostrarà la descripció sencera com a
   títol i deixarà el ponent en blanc.
4. Deixa passar fins a 4 hores (el cron de GitHub Actions sincronitza cada 4h), o
   força-ho ara mateix des de la pestanya **Actions** del repo → workflow
   *«Sync agenda from Nextcloud Calendar»* → **Run workflow**.

Les sessions amb data anterior a avui desapareixen soles de l'agenda (no cal
esborrar-les del calendari).

## Formularis d'assistència: es creen sols

En confirmar una sessió (pas 2 de dalt), el mateix sincronitzador li crea
automàticament un formulari d'assistència a Nextcloud Forms — **no cal crear-lo a
mà**:

- Es clona la plantilla «Confirmar asistencia — [Evento] · Speaker's Corner»
  (formulari amb id `3` a Nextcloud; si mai canvies les seves preguntes, els
  formularis nous ja les heretaran).
- El títol i la descripció es re-omplen amb l'esdeveniment, ponent, data, lloc i
  preu reals.
- Es tanca sol en arribar a **140 inscrits** o a l'hora d'inici de la xerrada (el
  que passi abans).
- El grup Nextcloud **`admins`** (Ajustes → Usuarios) pot veure sempre les
  respostes a la pestanya «Respuestas» del formulari, sense necessitat de ser-ne
  el propietari — afegeix-hi qui calgui des d'allà.
- L'URL de cada formulari es guarda a `data/agenda.json` (camp `form_url` de la
  sessió) i mai es torna a crear un segon formulari per al mateix esdeveniment.
- Si la creació falla per a una sessió concreta (Nextcloud caigut, etc.), queda
  registrat als logs del workflow i aquella targeta mostra l'avís «en preparació»
  fins al proper cicle de sincronització — la resta de l'agenda es publica igual.

Perquè això funcioni cal el secret de GitHub Actions `NEXTCLOUD_APP_PASSWORD`
(veure més avall).

## Canvis de data i cancel·lacions: també automàtics

- **Si canvies la data/hora** d'una sessió que ja tenia formulari, el
  sincronitzador li actualitza sol el títol, la descripció i el tancament
  (`expires`), i envia un correu (en `Cco`, un sol enviament) a totes les
  persones ja inscrites avisant del canvi. La inscripció es manté, no cal que
  tornin a apuntar-se.
- **Si elimines o desconfirmes** una sessió que encara no havia passat, el seu
  formulari es **tanca** (no s'esborra — les respostes queden per si calen) i
  s'envia un correu de cancel·lació a totes les persones inscrites.
- Una sessió que simplement **ja ha passat** no compta com a cancel·lada — no
  s'envia cap correu en aquest cas, és el comportament normal.
- Requereix, a més del secret anterior, `SMTP_PASSWORD` (veure més avall). Sense
  aquest segon secret, l'actualització del formulari es fa igualment; només
  s'omet l'enviament del correu.

- Sincronització manual (per provar-la fora del cron de GitHub Actions; sense la
  variable `NEXTCLOUD_APP_PASSWORD` no crea formularis nous, però sí actualitza
  l'agenda):
  ```bash
  cd scripts
  python3 -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  python sync_agenda.py
  ```
- Tests de l'script de sincronització: `pytest scripts/tests`
- Previsualitzar el lloc: obrir `index.html` directament al navegador, o servir la
  carpeta amb `python3 -m http.server` des de l'arrel del repo.
- Formulari «Vull ser speaker»: ja enllaçat a `js/app.js` (`FORM_URLS.speaker`).
  Newsletter: encara pendent — plantilla de preguntes a
  `docs/formularis-plantilla.md`.

## Secrets necessaris

**`NEXTCLOUD_APP_PASSWORD`** — perquè el workflow pugui crear/actualitzar/tancar
formularis a Nextcloud en nom de `admin`:

1. Nextcloud → Ajustes personales → Seguridad → «Crear nueva contraseña de
   aplicación».
2. Al repo de GitHub: `gh secret set NEXTCLOUD_APP_PASSWORD` (t'ho demanarà per
   `stdin`), o Settings → Secrets and variables → Actions → New repository
   secret.

**`SMTP_PASSWORD`** — perquè el workflow pugui avisar per correu els inscrits
d'un canvi de data o una cancel·lació. Reutilitza el mateix servidor de sortida
que ja té configurat Nextcloud (Ajustes básicos → Servidor de correo
electrónico: `smtp.gmail.com:465`, usuari `associaciocavecavet@gmail.com`) —
només cal la contrasenya (si Nextcloud hi té una contrasenya d'aplicació de
Gmail configurada, és la mateixa que va aquí):

```bash
gh secret set SMTP_PASSWORD --repo cavecavet/speakers-termes-montbrio
```

Sense `NEXTCLOUD_APP_PASSWORD`, la sincronització de l'agenda continua
funcionant amb normalitat — simplement no crea/actualitza/tanca formularis fins
que el secret existeixi. Sense `SMTP_PASSWORD`, els formularis es creen i
s'actualitzen igual, però no s'envia cap correu d'avís.
