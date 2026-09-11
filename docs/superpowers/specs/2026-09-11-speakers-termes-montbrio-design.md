# Speakers Corner Termes Montbrió — Cave Cavet · Diseño

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

1. **Hero** — títol «Speakers Corner Termes Montbrió · Cave Cavet», subtítol, pròxima
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
      "tipo": "gratuito"
    }
  ]
}
```

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

- `js/app.js` defineix `const FORM_URLS = { speaker: '#', newsletter: '#',
  sesion_generica: '#' }` a la capçalera del fitxer, amb un comentari indicant que
  cal substituir-ho per l'URL real de Nextcloud Forms o Google Forms.
- Els botons/enllaços del DOM porten `data-form="<clau>"`; un petit listener
  intercepta el clic i navega a `FORM_URLS[clau]` (obre en pestanya nova). Si l'URL
  és `#`, es mostra un avís «Formulario en preparación» en lloc de navegar.
- Es lliura per separat (fora del codi) una plantilla de preguntes suggerides per a
  cada formulari («Quiero ser speaker» i «Inscripción a sesión»), perquè l'usuari les
  creï manualment a Nextcloud Forms o Google Forms quan decideixi la plataforma.

## Publicació

- Repo `cavecavet/speakers-termes-montbrio` a GitHub (mateix patró que
  `espigo-cavet`), branch `main`, GitHub Pages activat des de `main` arrel.
- `CNAME` amb el contingut `speakers.cavecavet.org`.
- Cal que l'usuari afegeixi el registre DNS CNAME corresponent al seu proveïdor de
  domini (`cavecavet.org`) — fora de l'abast d'aquest agent.

## Testing / verificació

**`scripts/sync_agenda.py`** — únic component amb lògica no trivial: tests unitaris
(pytest) sobre fixtures `.ics` locals (no contra el calendari real) cobrint: filtratge
per `STATUS`, parsing de `Ponent:`/`Tema:` i el cas on la descripció no segueix el
format, ordenació determinista, i sortida buida quan no hi ha esdeveniments
confirmats.

**Lloc estàtic** — sense lògica de negoci complexa a testejar amb framework:
verificació manual amb el navegador de vista prèvia (Browser pane) sobre `index.html`
servit localment amb un `data/agenda.json` d'exemple:
- les seccions es veuen i l'agenda es renderitza des del JSON,
- l'estat buit («Pròximament noves sessions») es veu bé quan `sesiones` és `[]`,
- el canvi d'idioma CA/ES actualitza els textos fixos de la interfície,
- els botons de formulari mostren l'avís «en preparación» amb les URLs placeholder,
- comprovació visual en mòbil/escriptori (responsive) i que els dos logotips es
  llegeixen bé sobre els seus fons respectius.
