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

Un lloc estàtic d'una sola pàgina, sense dependències de build ni backend, que:
- presenti el cicle de xerrades amb la mateixa estructura de seccions que l'original,
- sigui fàcil d'actualitzar a mà (afegir una sessió = editar un JSON),
- permeti canviar de català a castellà,
- deixi preparats els punts d'enllaç cap a formularis externs (Nextcloud Forms o
  Google Forms, encara per decidir) sense necessitat de tocar l'HTML quan existeixin.

## Fora d'abast

- Venda/pagament en línia (WooCommerce): les sessions de pagament només mostren preu
  i enllacen a un formulari extern.
- Compte de YouTube propi: la secció de vídeos queda buida amb un «pròximament» fins
  que hi hagi contingut real.
- Creació dels formularis (Nextcloud Forms / Google Forms): fora de l'abast d'aquest
  agent, que no té accés a aquests comptes. S'inclou una plantilla de preguntes.
- Contingut real de sessions: es construeix amb dades d'exemple fàcils d'identificar
  i substituir.

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
├── data/agenda.json
├── logos/
│   ├── cavecavet.png            (copiat d'espigo-cavet/logos/)
│   └── termes-montbrio.webp     (copiat de ~/Desktop/LOGO-hotel-termes-montbrio-tarragona.webp)
└── CNAME                        # speakers.cavecavet.org
```

Sense frameworks, sense npm/build: obrir `index.html` directament o servir amb
qualsevol servidor estàtic n'hi ha prou per previsualitzar.

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

## Dades: `data/agenda.json`

```json
{
  "sesiones": [
    {
      "id": "2026-10-15-mindfulness",
      "fecha": "2026-10-15",
      "hora": "19:00",
      "titulo_ca": "Títol d'exemple en català",
      "titulo_es": "Título de ejemplo en castellano",
      "tipo": "gratuito",
      "precio": null,
      "ponente": "Nom del ponent (exemple)",
      "form_url_key": "sesion_generica"
    }
  ]
}
```

`app.js` ordena per `fecha`+`hora`, mostra les properes N sessions al hero/agenda, i
tria `titulo_ca`/`titulo_es` segons l'idioma actiu.

## i18n

- `js/i18n.js` exporta un diccionari `{ ca: {...}, es: {...} }` amb claus per a tots
  els textos estàtics de l'HTML (`data-i18n="hero.title"`, etc.).
- Un botó al header canvia `state.lang` (persistit a `localStorage`), re-renderitza
  els textos `data-i18n` i torna a pintar l'agenda amb `titulo_<lang>`.
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

No hi ha lògica de negoci complexa a testejar amb framework: verificació manual amb
el navegador de vista prèvia (Browser pane) sobre `index.html` servit localment:
- les seccions es veuen i l'agenda es renderitza des del JSON,
- el canvi d'idioma CA/ES actualitza tots els textos i els títols de sessió,
- els botons de formulari mostren l'avís «en preparación» amb les URLs placeholder,
- comprovació visual en mòbil/escriptori (responsive) i que els dos logotips es
  llegeixen bé sobre els seus fons respectius.
