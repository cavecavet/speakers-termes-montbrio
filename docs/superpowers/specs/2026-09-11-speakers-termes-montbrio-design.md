# Speaker's Corner Termes Montbrió — Cave Cavet · Diseño

## Contexto

L'Associació Cave Cavet i l'Hotel Termes Montbrió volen llançar un cicle de xerrades i
tallers propi, inspirat en el format «Speakers' Corner» de l'Hotel Roc Blanc
(https://rocblancspeakerscorner.net/). El lloc original és WordPress (tema premium
Betheme + WooCommerce + Contact Form 7): rèplica massa pesada per mantenir. Aquest
document defineix una versió lleugera, estàtica, amb la mateixa arquitectura de
seccions i un aspecte similar, amb la marca de l'Associació i de l'Hotel Termes
Montbrió.

## Objectiu

Un lloc estàtic d'una sola pàgina, sense backend en temps d'execució, que:
- presenti el cicle de xerrades amb la mateixa estructura de seccions que l'original,
- tingui una única font de veritat per a l'agenda: el calendari Nextcloud
  `Xerrades Hotel Termes Montbrió` que l'Associació ja fa servir — sense doble entrada
  de dades,
- permeti canviar de català a castellà,
- deixi preparats els punts d'enllaç cap a formularis externs (Nextcloud Forms o
  Google Forms, encara per decidir) sense necessitat de tocar l'HTML quan existeixin.

**Decisió (2026-09-11):** es va valorar allotjar tot el lloc a Nextcloud
(`cloud.cavecavet.org`, self-hosted en un Mac mini M4 de l'usuari). Descartat: els
enllaços públics de l'app Files de Nextcloud només serveixen un visor/descàrrega de
fitxers (per seguretat no executen HTML/CSS/JS pujat com una web real), així que no es
pot servir el disseny personalitzat en un domini net des d'allà. Nextcloud sí que
s'utilitza com a **font de dades** (Calendar) i, més endavant, per als formularis
(Forms). El lloc en si es manté a GitHub Pages.

## Fora d'abast

- Venda/pagament en línia (WooCommerce): les sessions de pagament només mostren preu
  i enllacen a un formulari extern.
- Compte de YouTube propi: la secció de vídeos queda buida amb un «pròximament» fins
  que hi hagi contingut real.
- Creació dels formularis (Nextcloud Forms / Google Forms): fora de l'abast d'aquest
  agent, que no té accés a aquests comptes. S'inclou una plantilla de preguntes.
- Preu/gratuïtat per sessió: el calendari no ho registra com a camp; totes les
  sessions sincronitzades es mostren com a gratuïtes de moment (es pot afegir un preu
  manualment més endavant si cal).
- Al mockup de disseny (aprovat visualment) s'hi va usar contingut d'exemple; el lloc
  final mostra les sessions reals confirmades del calendari (pot no haver-n'hi cap al
  moment de publicar, i llavors l'agenda es mostra buida amb un missatge).

## Arquitectura

Repositori nou `cavecavet/speakers-termes-montbrio` (patró idèntic a `espigo-cavet`:
sense build, publicat amb GitHub Pages + `CNAME`).

```
speakers-termes-montbrio/
├── index.html
├── css/style.css
├── js/
│   ├── app.js          # renderitza l'agenda des de data/agenda.json
│   └── i18n.js          # diccionari CA/ES + canvi d'idioma
├── data/agenda.json     # generat per l'script de sincronització (no s'edita a mà)
├── scripts/
│   ├── sync_agenda.py   # descarrega l'.ics públic i regenera data/agenda.json
│   └── requirements.txt # icalendar
├── .github/workflows/sync-agenda.yml   # cron cada 4h + commit automàtic si canvia
├── logos/
│   ├── cavecavet.png            (copiat d'espigo-cavet/logos/)
│   └── termes-montbrio.webp     (copiat de ~/Desktop/LOGO-hotel-termes-montbrio-tarragona.webp)
└── CNAME                        # speakers.cavecavet.org
```

El lloc en si (`index.html` + `css/` + `js/`) segueix sense frameworks ni npm/build:
obrir-lo directament o servir-lo amb qualsevol servidor estàtic n'hi ha prou per
previsualitzar. L'única peça no-estàtica és l'script Python de sincronització, que
corre a GitHub Actions (no al navegador del visitant) i simplement escriu un fitxer
JSON pla al repo.

## Tractament visual

- **Header/nau i hero**: fons fosc navy/carbó. A l'esquerra només la **icona** del
  pop de Cave Cavet (el text del logotip complet és negre i no es llegeix sobre fons
  fosc); a la dreta el logotip de Termes Montbrió en blanc (ja pensat per fons fosc).
- **Secció «Qui organitza»**: franja de fons clar (blanc/gris molt clar) amb el
  lockup complet de Cave Cavet (icona + text) i el logo de Termes Montbrió.
- **Paleta**: base navy/carbó fosc (`#1c1d22`-ish) + blanc, accent càlid daurat/mostassa
  per CTAs i badges (coherent amb l'original, sense competir amb el blau del pop ni
  amb el blanc del logo de l'hotel).
- **Tipografia**: sans-serif de sistema o Google Font lliure (p. ex. Inter/Barlow),
  sense dependència de fonts de pagament.

## Seccions de contingut (una sola pàgina, navegació per àncores)

1. **Hero** — títol «Speaker's Corner Termes Montbrió · Cave Cavet», subtítol, pròxima
   sessió destacada, botons «Ver la agenda» / «Quiero ser speaker».
2. **Agenda** — targetes de pròximes sessions generades des de `agenda.json`
   (data, hora, títol, gratis/preu, botó d'inscripció).
3. **¿Quieres ser speaker?** — CTA amb botó cap al formulari (`data-form="speaker"`).
4. **Vídeos/Podcast** — buida amb «pròximament» fins que hi hagi contingut.
5. **Newsletter** — formulari/CTA (`data-form="newsletter"`).
6. **Sobre la iniciativa** — Associació + Hotel, lockup complet dels dos logos.
7. **Contacte** — dades de contacte de l'Associació.

## Font de dades: calendari Nextcloud

- Calendari `Xerrades Hotel Termes Montbrió`, compartit públicament amb el token
  `RP5xH59a33ZBNwLx`. Feed `.ics` verificat accessible de forma anònima (200 OK, sense
  autenticació) a:
  `https://cloud.cavecavet.org/remote.php/dav/public-calendars/RP5xH59a33ZBNwLx?export`
- Aquest feed **no envia capçalera CORS**, així que no es pot fer `fetch()` en viu des
  del navegador d'un visitant a `speakers.cavecavet.org` (origen diferent). Per això la
  descàrrega es fa en una GitHub Action (servidor a servidor, sense restricció CORS),
  no en temps real al navegador.
- Format de la descripció de cada esdeveniment (acordat amb l'usuari, s'ha de mantenir
  sempre igual perquè l'script el pugui parsejar):
  ```
  Ponent: <nom>
  Tema: <títol de la xerrada>
  ```
  Si un esdeveniment no segueix aquest format, l'script hi posa la descripció completa
  tal qual com a títol i deixa `ponente` buit.
- Només es publiquen esdeveniments amb `STATUS:CONFIRMED` a l'`.ics` (els marcats
  `TENTATIVE`/"provisional" a la UI de Nextcloud queden fora fins que es confirmin).
- Camps ICS usats per esdeveniment: `SUMMARY` (es descarta, és el nom de treball
  intern), `DTSTART`/`DTEND`, `LOCATION`, `DESCRIPTION` (parsejada com s'ha dit),
  `STATUS`, `UID` (com a `id` estable).

## `data/agenda.json` (generat, no editable a mà)

```json
{
  "generated_at": "2026-09-11T15:20:00Z",
  "source": "https://cloud.cavecavet.org/remote.php/dav/public-calendars/RP5xH59a33ZBNwLx?export",
  "sesiones": [
    {
      "id": "<UID de l'esdeveniment>",
      "fecha": "2026-10-15",
      "hora": "19:00",
      "titulo": "Beneficis de l'aigua i del mar per a la salut i el sistema nerviós",
      "ponente": "Mercè Milán",
      "lugar": "Hotel Termes de Montbrió",
      "tipo": "gratuito",
      "form_url": "https://cloud.cavecavet.org/apps/forms/s/<hash>"
    }
  ]
}
```

`form_url` és `null` fins que el sincronitzador li crea el formulari d'assistència
(vegeu «Formularis d'assistència per sessió» més avall) — un cop assignat, mai es
torna a sobreescriure per a aquest mateix `id` de sessió.

Com que el calendari només guarda el text en un idioma, les sessions sincronitzades
**no tenen versió `_ca`/`_es` separada**: es mostren amb el mateix text sigui quin
sigui l'idioma triat a la interfície (només canvien les etiquetes fixes del lloc —
«Inscripció»/«Inscripción», «Gratuït»/«Gratuito», etc.). `app.js` ordena per
`fecha`+`hora` i mostra les properes sessions al hero/agenda; si `sesiones` és buit,
la secció mostra un missatge «Pròximament noves sessions» en lloc d'una llista buida.

## Sincronització (`scripts/sync_agenda.py` + GitHub Action)

- L'script descarrega l'`.ics`, el parseja amb la llibreria `icalendar`, filtra
  `STATUS:CONFIRMED`, aplica el parsing de `Ponent:`/`Tema:`, i escriu
  `data/agenda.json` amb sortida determinista (mateix ordre sempre) perquè els diffs
  de git siguin nets.
- El workflow `.github/workflows/sync-agenda.yml` corre amb `schedule: cron` cada 4
  hores (coincidint amb el `REFRESH-INTERVAL:PT4H` que ja publica el propi calendari)
  més `workflow_dispatch` per poder-lo llançar a mà. Si `data/agenda.json` canvia,
  fa `git commit` + `git push` a `main`; GitHub Pages republica automàticament. Si no
  hi ha canvis, no fa cap commit buit.
- Res d'això toca el navegador del visitant: el lloc publicat sempre serveix un
  `agenda.json` ja generat, estàtic.

## i18n

- `js/i18n.js` exporta un diccionari `{ ca: {...}, es: {...} }` amb claus per a tots
  els textos estàtics de l'HTML (`data-i18n="hero.title"`, etc.).
- Un botó al header canvia `state.lang` (persistit a `localStorage`) i re-renderitza
  els textos `data-i18n`; les targetes d'agenda no canvien de text (vegeu «Font de
  dades»), només les etiquetes fixes que les envolten.
- Idioma per defecte: català; si `localStorage` no té preferència, es manté català
  (no es detecta l'idioma del navegador per mantenir-ho predictible).

## Integració de formularis

- `js/app.js` defineix `const FORM_URLS = { speaker: <URL real>, newsletter: '#',
  sesion_generica: '#' }`. `speaker` ja apunta al formulari real de Nextcloud Forms
  (`https://cloud.cavecavet.org/apps/forms/s/2LJptgTKoXNtGRTKfEZMqcjT`).
- Els botons/enllaços del DOM porten `data-form="<clau>"` i, quan la sessió té un
  formulari propi, també `data-url="<url>"`. Un listener (`wireFormLinks`)
  intercepta el clic: usa `data-url` si existeix, si no cau a
  `FORM_URLS[data-form]`; si el resultat és buit o `#`, mostra l'avís «Formulario en
  preparación» en lloc de navegar.
- Newsletter: encara pendent de crear (plantilla a `docs/formularis-plantilla.md`).

### Formularis d'assistència per sessió — generats automàticament (decisió 2026-09-12)

Cada sessió confirmada té el seu propi formulari d'inscripció a Nextcloud Forms,
creat pel mateix `scripts/sync_agenda.py` en comptes de manualment:

- **Plantilla**: formulari `id=3` a Nextcloud («Confirmar asistencia — [Evento] ·
  Speaker's Corner», 5 preguntes: nom, correu, nombre d'assistents, telèfon
  opcional, acceptació de política de privacitat). Es clona per API
  (`POST /forms?fromId=3`) — mai es recreen les preguntes des de zero.
- **Tancament automàtic**: `expires` = timestamp exacte d'inici de la xerrada
  (Europe/Madrid) i `maxSubmissions = 140` — el formulari deixa d'acceptar
  respostes en arribar qualsevol dels dos límits, el que passi primer. Cap
  d'aquests dos camps apareix documentat a `docs/DataStructure.md` del propi
  projecte Forms, però es va confirmar empíricament (GET real sobre un formulari
  de prova) que `maxSubmissions` és un camp vàlid de l'API v3.
- **Accés dels administradors**: grup Nextcloud `admins` (creat expressament,
  membres inicials `admin` i `estela`) rep un share de tipus grup amb
  `permissions: ["submit", "results"]` — **cal enviar els dos permisos junts**;
  provar només `["results"]` retorna `400 Invalid permission given` (confirmat
  contra la instància real).
- **Idempotència**: `data/agenda.json` guarda `form_url` per sessió. En cada
  sincronització, una sessió que ja tenia `form_url` el manté sense tornar a
  trucar l'API (encara que altres camps seus hagin canviat); només es crea un
  formulari nou per a un `id` de sessió que mai n'ha tingut cap.
- **Degradació**: si `NEXTCLOUD_APP_PASSWORD` no existeix (execucions locals sense
  el secret), `form_url` queda `null` i l'agenda es sincronitza igualment — no cal
  el secret per treballar en local. Si la creació falla per a una sessió concreta,
  es registra l'error i la resta de sessions es processen igual (no atura tot el
  sync).
- **Autenticació**: Basic Auth amb l'usuari `admin` i una contrasenya d'aplicació
  (mai la contrasenya real) guardada com a secret de GitHub Actions
  `NEXTCLOUD_APP_PASSWORD` — l'usuari la genera i la desa ell mateix
  (`gh secret set`), mai passa per aquesta conversa ni pel codi.
- **Backfill manual (2026-09-12)**: el formulari ja existent de Mercè Milán (creat
  a mà abans d'aquesta automatització) es va actualitzar amb els mateixos límits
  (`expires`, `maxSubmissions=140`, share al grup `admins`) i la seva `form_url`
  real es va desar directament a `data/agenda.json`, perquè l'script no torni a
  intentar crear-ne un altre per a aquest esdeveniment.

## Publicació

- Repo `cavecavet/speakers-termes-montbrio` a GitHub (mateix patró que
  `espigo-cavet`), branch `main`, GitHub Pages activat des de `main` arrel. **Fet i
  en producció** a https://speakers.cavecavet.org/.
- `CNAME` amb el contingut `speakers.cavecavet.org`.
- DNS: registre CNAME `speakers.cavecavet.org` → `cavecavet.github.io` a
  Cloudflare, **proxied** (nube naranja) — seguint el mateix patró que `espigo` i
  `exposicions`, els altres dos subdominis d'aquest compte que ja apunten a
  `cavecavet.github.io`. Fet el 2026-09-11.

## Testing / verificació

**`scripts/sync_agenda.py`** — únic component amb lògica no trivial: tests unitaris
(pytest) sobre fixtures `.ics` locals (no contra el calendari real) cobrint: filtratge
per `STATUS`, parsing de `Ponent:`/`Tema:` i el cas on la descripció no segueix el
format, ordenació determinista, i sortida buida quan no hi ha esdeveniments
confirmats. La part de formularis té dues capes de test: les funcions pures
(`build_form_title`, `build_form_description`, `format_session_datetime`,
`session_price_label`, `session_expiry_timestamp`) i `attach_form_urls` (amb
`ensure_attendance_form` mockejat, per verificar reutilització/creació/degradació
sense tocar la xarxa); i un test d'`ensure_attendance_form` amb `urlopen` mockejat
que verifica la seqüència exacta clona→PATCH→share públic→share de grup i els
`body` enviats a cadascuna, contra el contracte real ja validat a mà (2026-09-12)
sobre la instància de producció.

**Lloc estàtic** — sense lògica de negoci complexa a testejar amb framework:
verificació manual amb el navegador de vista prèvia (Browser pane) sobre `index.html`
servit localment amb un `data/agenda.json` d'exemple:
- les seccions es veuen i l'agenda es renderitza des del JSON,
- l'estat buit («Pròximament noves sessions») es veu bé quan `sesiones` és `[]`,
- el canvi d'idioma CA/ES actualitza els textos fixos de la interfície,
- els botons de formulari mostren l'avís «en preparación» amb les URLs placeholder,
- comprovació visual en mòbil/escriptori (responsive) i que els dos logotips es
  llegeixen bé sobre els seus fons respectius.
