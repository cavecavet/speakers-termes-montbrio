# Speakers Corner Termes Montbrió Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and publish a static one-page site for the "Speakers Corner Termes Montbrió · Cave Cavet" talks cycle, with its agenda synced automatically from an existing Nextcloud Calendar.

**Architecture:** Plain HTML/CSS/JS, no build step, hosted on GitHub Pages (`speakers.cavecavet.org`). A Python script run on a schedule by a GitHub Action downloads the public `.ics` export of the `Xerrades Hotel Termes Montbrió` Nextcloud calendar, filters confirmed sessions, and writes `data/agenda.json`; the page's own JS only ever reads that already-generated JSON file — no CORS-restricted network call ever happens in the visitor's browser.

**Tech Stack:** HTML/CSS/vanilla JS (no framework, no npm), Python 3.12 + `icalendar` for the sync script, `pytest` for the script's tests, GitHub Actions for scheduling, GitHub Pages for hosting.

**Spec:** `docs/superpowers/specs/2026-09-11-speakers-termes-montbrio-design.md`

## Global Constraints

- Repo name: `speakers-termes-montbrio`, GitHub org `cavecavet` (same org as `espigo-cavet`).
- `CNAME` content: `speakers.cavecavet.org` (exact, no trailing content).
- Calendar feed URL (public, no auth needed — verified 200 OK): `https://cloud.cavecavet.org/remote.php/dav/public-calendars/RP5xH59a33ZBNwLx?export`.
- Only events with `STATUS:CONFIRMED` in the `.ics` are published; everything else (including `TENTATIVE`/no status) is excluded.
- Event description must follow `Ponent: <nom>\nTema: <títol>`; when absent, use the full description as `titulo` and leave `ponente` empty.
- Every synced session's `tipo` is hardcoded to `"gratuito"` (no price field exists yet).
- Default UI language is Catalan (`ca`); no browser-language detection — only an explicit user click (persisted in `localStorage`) changes it.
- Form buttons carry `data-form="speaker" | "newsletter" | "sesion_generica"`; until real URLs exist, clicking shows an alert instead of navigating.
- Visual tokens (already approved, from `preview/mockup.html`): fonts Fraunces/Work Sans/IBM Plex Mono via Google Fonts; colors `--ink:#171b22`, `--ink-soft:#232a36`, `--ink-line:#333b49`, `--stone:#e8ece8`, `--stone-soft:#f5f7f4`, `--stone-line:#c9d1cb`, `--brass:#c69a4d`, `--brass-ink:#3a2c10`, `--teal:#3f93a1`.
- Logos already copied into the repo at `logos/cavecavet.png` and `logos/termes-montbrio.webp` — do not re-fetch or modify them.

---

### Task 1: Repo scaffold

**Files:**
- Create: `.gitignore`
- Create: `README.md`
- Verify (already present from the design phase): `logos/cavecavet.png`, `logos/termes-montbrio.webp`, `CNAME`, `docs/superpowers/specs/2026-09-11-speakers-termes-montbrio-design.md`

**Interfaces:**
- Produces: the directory skeleton every later task writes into (`data/`, `scripts/`, `css/`, `js/`, `.github/workflows/`).

- [ ] **Step 1: Confirm the repo root and existing files**

Run:
```bash
cd ~/Documents/GitHub/speakers-termes-montbrio
ls -la
cat CNAME
```
Expected: `CNAME` contains exactly `speakers.cavecavet.org` (no trailing newline issues), and `logos/cavecavet.png` + `logos/termes-montbrio.webp` exist. If `CNAME` is missing, create it:
```bash
printf 'speakers.cavecavet.org' > CNAME
```

- [ ] **Step 2: Create `.gitignore`**

```
__pycache__/
*.pyc
.venv/
.DS_Store
```

- [ ] **Step 3: Create the directory skeleton**

```bash
mkdir -p data scripts/tests css js .github/workflows
```

- [ ] **Step 4: Write `README.md`**

```markdown
# Speakers Corner Termes Montbrió

Lloc estàtic (sense build) del cicle de xerrades organitzat per l'Associació Cave
Cavet i l'Hotel Termes Montbrió. Publicat a `speakers.cavecavet.org` via GitHub
Pages.

- Disseny i decisions: `docs/superpowers/specs/2026-09-11-speakers-termes-montbrio-design.md`
- L'agenda (`data/agenda.json`) es genera automàticament — **no s'edita a mà**. La
  font és el calendari Nextcloud `Xerrades Hotel Termes Montbrió`
  (`https://cloud.cavecavet.org/apps/calendar/p/RP5xH59a33ZBNwLx`); només es
  publiquen els esdeveniments marcats com a confirmats.
- Sincronització manual (per provar-la fora del cron de GitHub Actions):
  ```bash
  cd scripts
  python3 -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  python sync_agenda.py
  ```
- Tests de l'script de sincronització: `pytest scripts/tests`
- Previsualitzar el lloc: obrir `index.html` directament al navegador, o servir la
  carpeta amb `python3 -m http.server` des de l'arrel del repo.
```

- [ ] **Step 5: Write the forms question template (spec deliverable, not code)**

Create `docs/formularis-plantilla.md`:

```markdown
# Plantilla de preguntes per als formularis

Per crear manualment a Nextcloud Forms o Google Forms (l'agent no té accés a cap
dels dos comptes). Un cop creat, enganxa l'URL resultant a `FORM_URLS` dins de
`js/app.js` (claus `speaker` / `newsletter` / `sesion_generica`).

## «Vull ser speaker» (clau `speaker`)

1. Nom i cognoms
2. Correu electrònic de contacte
3. Telèfon (opcional)
4. Tema o títol provisional de la xerrada/taller
5. Breu descripció (2-3 frases) del contingut
6. Durada aproximada
7. Necessitats tècniques (projector, música, espai per moure's, etc.)
8. Disponibilitat (mesos/dies de la setmana que et van bé)

## Inscripció a una sessió (clau `sesion_generica`)

1. Nom i cognoms
2. Correu electrònic
3. Sessió a la qual t'inscrius (desplegable o text lliure amb la data/títol)
4. Nombre d'acompanyants (si s'admeten)
5. Ets hoste de l'Hotel Termes Montbrió? (sí/no)
6. Acceptació de la política de privacitat

## Newsletter (clau `newsletter`)

1. Nom
2. Correu electrònic
3. Acceptació de la política de privacitat
```

- [ ] **Step 6: Commit**

```bash
git add .gitignore README.md CNAME docs/formularis-plantilla.md
git commit -m "chore: scaffold repo structure, README, and forms question template"
```

---

### Task 2: `parse_description` helper (TDD)

**Files:**
- Create: `scripts/sync_agenda.py`
- Test: `scripts/tests/test_sync_agenda.py`

**Interfaces:**
- Produces: `parse_description(description: str) -> tuple[str, str]` — returns `(titulo, ponente)`.

- [ ] **Step 1: Write the failing tests**

```python
# scripts/tests/test_sync_agenda.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sync_agenda import parse_description


def test_parse_description_extracts_ponent_and_tema():
    description = (
        "Ponència · Agenda provisional (pendent de confirmació).\n\n"
        "Ponent: Mercè Milán\n"
        "Tema: Beneficis de l'aigua i del mar per a la salut i el sistema nerviós. "
        "Recepta blava i Blue Mind.\n\n"
        "Hotel Termes de Montbrió — Proposta Associació Cave Cavet."
    )
    titulo, ponente = parse_description(description)
    assert ponente == "Mercè Milán"
    assert titulo == (
        "Beneficis de l'aigua i del mar per a la salut i el sistema nerviós. "
        "Recepta blava i Blue Mind."
    )


def test_parse_description_falls_back_when_pattern_absent():
    description = "Xerrada oberta sobre gestió del temps, sense format estàndard."
    titulo, ponente = parse_description(description)
    assert titulo == "Xerrada oberta sobre gestió del temps, sense format estàndard."
    assert ponente == ""


def test_parse_description_handles_empty_string():
    titulo, ponente = parse_description("")
    assert titulo == ""
    assert ponente == ""
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd scripts && python3 -m pytest tests/test_sync_agenda.py -v`
Expected: `ModuleNotFoundError: No module named 'sync_agenda'` (the file doesn't exist yet).

- [ ] **Step 3: Write `scripts/sync_agenda.py` with just this function**

```python
"""Sync data/agenda.json from the public Nextcloud Calendar export."""


def parse_description(description: str) -> tuple[str, str]:
    """Extract (titulo, ponente) from a 'Ponent: X' / 'Tema: Y' description.

    Falls back to (description.strip(), "") when the pattern is absent.
    """
    ponente = ""
    titulo = ""
    for line in (description or "").splitlines():
        line = line.strip()
        if line.lower().startswith("ponent:"):
            ponente = line.split(":", 1)[1].strip()
        elif line.lower().startswith("tema:"):
            titulo = line.split(":", 1)[1].strip()
    if titulo:
        return titulo, ponente
    return (description or "").strip(), ""
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd scripts && python3 -m pytest tests/test_sync_agenda.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/sync_agenda.py scripts/tests/test_sync_agenda.py
git commit -m "feat: parse speaker/topic out of calendar event descriptions"
```

---

### Task 3: `parse_sessions` (ICS parsing, filtering, sorting) (TDD)

**Files:**
- Modify: `scripts/sync_agenda.py`
- Modify: `scripts/tests/test_sync_agenda.py`
- Create: `scripts/requirements.txt`

**Interfaces:**
- Consumes: `parse_description(description: str) -> tuple[str, str]` from Task 2.
- Produces: `parse_sessions(ics_bytes: bytes) -> list[dict]`, each dict shaped `{"id", "fecha", "hora", "titulo", "ponente", "lugar", "tipo"}`, sorted ascending by `(fecha, hora)`, containing only `STATUS:CONFIRMED` events.

- [ ] **Step 1: Create `scripts/requirements.txt`**

```
icalendar>=5.0
pytest>=7.0
```

- [ ] **Step 2: Install dependencies**

```bash
cd scripts
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- [ ] **Step 3: Write the failing tests**

Append to `scripts/tests/test_sync_agenda.py`:

```python
from sync_agenda import parse_sessions

CONFIRMED_EVENT = """BEGIN:VEVENT
UID:evt-confirmed-1@cavecavet.org
DTSTAMP:20260901T090000Z
DTSTART;TZID=Europe/Madrid:20261015T190000
DTEND;TZID=Europe/Madrid:20261015T194500
SUMMARY:Speakers' Corner · Mercè Milán
LOCATION:Hotel Termes de Montbrió
DESCRIPTION:Ponent: Mercè Milán\\nTema: El silenci com a eina de benestar
STATUS:CONFIRMED
END:VEVENT
"""

TENTATIVE_EVENT = """BEGIN:VEVENT
UID:evt-tentative-1@cavecavet.org
DTSTAMP:20260901T090000Z
DTSTART;TZID=Europe/Madrid:20261005T110000
DTEND;TZID=Europe/Madrid:20261005T114500
SUMMARY:Speakers' Corner · Estela Trenado (provisional)
LOCATION:Hotel Termes de Montbrió
DESCRIPTION:Ponent: Estela Trenado\\nTema: Encara per confirmar
STATUS:TENTATIVE
END:VEVENT
"""

CONFIRMED_NO_PATTERN_EVENT = """BEGIN:VEVENT
UID:evt-confirmed-2@cavecavet.org
DTSTAMP:20260901T090000Z
DTSTART;TZID=Europe/Madrid:20261005T180000
DTEND;TZID=Europe/Madrid:20261005T184500
SUMMARY:Speakers' Corner · sessió oberta
LOCATION:Hotel Termes de Montbrió
DESCRIPTION:Xerrada oberta sobre gestió del temps\\, sense format estàndard.
STATUS:CONFIRMED
END:VEVENT
"""

VCALENDAR_HEADER = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//Test//EN
BEGIN:VTIMEZONE
TZID:Europe/Madrid
BEGIN:DAYLIGHT
TZNAME:CEST
TZOFFSETFROM:+0100
TZOFFSETTO:+0200
DTSTART:19700329T020000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU
END:DAYLIGHT
BEGIN:STANDARD
TZNAME:CET
TZOFFSETFROM:+0200
TZOFFSETTO:+0100
DTSTART:19701025T030000
RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU
END:STANDARD
END:VTIMEZONE
"""

VCALENDAR_FOOTER = "END:VCALENDAR\n"


def make_ics(*events: str) -> bytes:
    return (VCALENDAR_HEADER + "".join(events) + VCALENDAR_FOOTER).encode("utf-8")


def test_parse_sessions_includes_only_confirmed_events():
    ics_bytes = make_ics(CONFIRMED_EVENT, TENTATIVE_EVENT)
    sessions = parse_sessions(ics_bytes)
    assert len(sessions) == 1
    assert sessions[0]["id"] == "evt-confirmed-1@cavecavet.org"


def test_parse_sessions_maps_fields_correctly():
    ics_bytes = make_ics(CONFIRMED_EVENT)
    session = parse_sessions(ics_bytes)[0]
    assert session == {
        "id": "evt-confirmed-1@cavecavet.org",
        "fecha": "2026-10-15",
        "hora": "19:00",
        "titulo": "El silenci com a eina de benestar",
        "ponente": "Mercè Milán",
        "lugar": "Hotel Termes de Montbrió",
        "tipo": "gratuito",
    }


def test_parse_sessions_falls_back_when_description_has_no_pattern():
    ics_bytes = make_ics(CONFIRMED_NO_PATTERN_EVENT)
    session = parse_sessions(ics_bytes)[0]
    assert session["titulo"] == "Xerrada oberta sobre gestió del temps, sense format estàndard."
    assert session["ponente"] == ""


def test_parse_sessions_sorts_by_date_then_time():
    ics_bytes = make_ics(CONFIRMED_EVENT, CONFIRMED_NO_PATTERN_EVENT)
    sessions = parse_sessions(ics_bytes)
    assert [s["id"] for s in sessions] == [
        "evt-confirmed-2@cavecavet.org",
        "evt-confirmed-1@cavecavet.org",
    ]


def test_parse_sessions_returns_empty_list_when_nothing_confirmed():
    ics_bytes = make_ics(TENTATIVE_EVENT)
    assert parse_sessions(ics_bytes) == []
```

- [ ] **Step 4: Run the tests to verify they fail**

Run: `cd scripts && python3 -m pytest tests/test_sync_agenda.py -v`
Expected: `ImportError: cannot import name 'parse_sessions'`.

- [ ] **Step 5: Implement `parse_sessions`**

Append to `scripts/sync_agenda.py`:

```python
from icalendar import Calendar


def parse_sessions(ics_bytes: bytes) -> list[dict]:
    """Parse calendar bytes into CONFIRMED sessions, sorted by fecha+hora."""
    calendar = Calendar.from_ical(ics_bytes)
    sessions = []
    for component in calendar.walk("VEVENT"):
        status = str(component.get("status", "")).upper()
        if status != "CONFIRMED":
            continue
        dtstart = component.get("dtstart").dt
        titulo, ponente = parse_description(str(component.get("description", "")))
        sessions.append(
            {
                "id": str(component.get("uid", "")),
                "fecha": dtstart.strftime("%Y-%m-%d"),
                "hora": dtstart.strftime("%H:%M"),
                "titulo": titulo,
                "ponente": ponente,
                "lugar": str(component.get("location", "")),
                "tipo": "gratuito",
            }
        )
    sessions.sort(key=lambda s: (s["fecha"], s["hora"]))
    return sessions
```

Move the `from icalendar import Calendar` line to the top of the file with the module docstring, above `parse_description`.

- [ ] **Step 6: Run the tests to verify they pass**

Run: `cd scripts && python3 -m pytest tests/test_sync_agenda.py -v`
Expected: 8 passed.

- [ ] **Step 7: Commit**

```bash
git add scripts/sync_agenda.py scripts/tests/test_sync_agenda.py scripts/requirements.txt
git commit -m "feat: parse confirmed sessions out of the ICS calendar feed"
```

---

### Task 4: `build_agenda`, `fetch_ics`, `main()` and first real sync (TDD + manual run)

**Files:**
- Modify: `scripts/sync_agenda.py`
- Modify: `scripts/tests/test_sync_agenda.py`
- Create (generated by running the script for real): `data/agenda.json`

**Interfaces:**
- Consumes: `parse_sessions(ics_bytes: bytes) -> list[dict]` from Task 3.
- Produces: `build_agenda(ics_bytes: bytes, source_url: str, generated_at: str) -> dict`, `fetch_ics(url: str) -> bytes`, `main() -> int`.

- [ ] **Step 1: Write the failing test for `build_agenda`**

Append to `scripts/tests/test_sync_agenda.py`:

```python
from sync_agenda import build_agenda


def test_build_agenda_wraps_sessions_with_metadata():
    ics_bytes = make_ics(CONFIRMED_EVENT)
    agenda = build_agenda(ics_bytes, "https://example.org/feed.ics", "2026-09-11T15:00:00Z")
    assert agenda["source"] == "https://example.org/feed.ics"
    assert agenda["generated_at"] == "2026-09-11T15:00:00Z"
    assert len(agenda["sesiones"]) == 1
    assert agenda["sesiones"][0]["id"] == "evt-confirmed-1@cavecavet.org"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd scripts && python3 -m pytest tests/test_sync_agenda.py -v`
Expected: `ImportError: cannot import name 'build_agenda'`.

- [ ] **Step 3: Implement `build_agenda`, `fetch_ics` and `main`**

Append to `scripts/sync_agenda.py`:

```python
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ICS_URL = "https://cloud.cavecavet.org/remote.php/dav/public-calendars/RP5xH59a33ZBNwLx?export"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "agenda.json"


def build_agenda(ics_bytes: bytes, source_url: str, generated_at: str) -> dict:
    return {
        "generated_at": generated_at,
        "source": source_url,
        "sesiones": parse_sessions(ics_bytes),
    }


def fetch_ics(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read()


def main() -> int:
    ics_bytes = fetch_ics(ICS_URL)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    agenda = build_agenda(ics_bytes, ICS_URL, generated_at)
    new_sessions = agenda["sesiones"]

    old_sessions = None
    if OUTPUT_PATH.exists():
        try:
            old_sessions = json.loads(OUTPUT_PATH.read_text(encoding="utf-8")).get("sesiones")
        except json.JSONDecodeError:
            old_sessions = None

    if old_sessions == new_sessions:
        print("agenda.json sense canvis (sessions idèntiques), no s'escriu res de nou.")
        return 0

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(agenda, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"agenda.json actualitzat amb {len(new_sessions)} sessions confirmades.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Move the `import` lines (`json`, `sys`, `urllib.request`, `datetime`, `Path`) to the top of the file alongside the existing `icalendar` import.

- [ ] **Step 4: Run all tests to verify they pass**

Run: `cd scripts && python3 -m pytest tests/ -v`
Expected: 9 passed.

- [ ] **Step 5: Run the script for real against the live calendar**

```bash
cd ~/Documents/GitHub/speakers-termes-montbrio
python3 scripts/sync_agenda.py
cat data/agenda.json
```
Expected: exit code 0, a message printed, and `data/agenda.json` created. As of this writing every real event in the calendar is `(provisional)`/tentative, so `sesiones` is likely `[]` — that's correct behavior, not a bug (Task 9 covers testing the populated-list rendering with a temporary local fixture).

- [ ] **Step 6: Commit**

```bash
git add scripts/sync_agenda.py scripts/tests/test_sync_agenda.py data/agenda.json
git commit -m "feat: fetch the live calendar feed and write data/agenda.json"
```

---

### Task 5: GitHub Actions workflow to run the sync on a schedule

**Files:**
- Create: `.github/workflows/sync-agenda.yml`

**Interfaces:**
- Consumes: `scripts/sync_agenda.py` (Task 4) and `scripts/requirements.txt` (Task 3).

- [ ] **Step 1: Write the workflow**

```yaml
name: Sync agenda from Nextcloud Calendar

on:
  schedule:
    - cron: "0 */4 * * *"
  workflow_dispatch: {}

permissions:
  contents: write

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install -r scripts/requirements.txt

      - name: Run sync script
        run: python scripts/sync_agenda.py

      - name: Commit changes if any
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add data/agenda.json
          if git diff --cached --quiet; then
            echo "No hi ha canvis a l'agenda."
          else
            git commit -m "chore: sync agenda from Nextcloud Calendar"
            git push
          fi
```

- [ ] **Step 2: Validate the YAML syntax locally**

```bash
python3 -c "import yaml, sys; yaml.safe_load(open('.github/workflows/sync-agenda.yml')); print('YAML ok')"
```
Expected: `YAML ok` (if `pyyaml` isn't installed, `pip install pyyaml` first, or skip and rely on GitHub's own validation after push in Task 10).

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/sync-agenda.yml
git commit -m "ci: schedule agenda sync every 4 hours"
```

---

### Task 6: Static page shell — `index.html` + `css/style.css`

**Files:**
- Create: `index.html`
- Create: `css/style.css`
- Delete: `preview/mockup.html` (superseded by `index.html`)

**Interfaces:**
- Produces: the DOM hooks later tasks depend on — element ids `hero-ticket` (with children marked `data-slot="date|title|who|cta"`), `agenda-list`, `agenda-empty`; `.lang-toggle button[data-lang]`; any clickable element needing `data-form="speaker"|"newsletter"|"sesion_generica"`.
- Consumes: `logos/cavecavet.png`, `logos/termes-montbrio.webp` (already in repo).

- [ ] **Step 1: Create `css/style.css`**

Copy the entire contents of the `<style>` block from `preview/mockup.html` (lines between `<style>` and `</style>`, exclusive) verbatim into `css/style.css` — no changes needed, it's already the approved visual design. Then add these two rules at the end (mobile nav is already `display:none`; this makes the empty-state box reusable for the agenda section, reusing the existing `.video-empty` look):

```css
#agenda-empty{margin-top:1rem;}
.badge-preview{display:none;}
```

(The second rule keeps the file forward-compatible in case `index.html` is ever cloned from the mockup again with the badge still in it; `index.html` itself will not include that badge markup at all — see Step 2.)

- [ ] **Step 2: Create `index.html`**

```html
<!doctype html>
<html lang="ca">
<head>
<meta charset="utf-8">
<title>Speakers Corner Termes Montbrió</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Work+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/style.css">
</head>
<body>

<header>
  <nav>
    <div class="brand">
      <img src="logos/cavecavet.png" alt="Associació Cave Cavet" style="object-fit:cover;object-position:0 0;width:36px;height:36px;">
      <div class="brand-name">Speakers Corner<small data-i18n="nav.tag">Termes Montbrió · Cave Cavet</small></div>
    </div>
    <div class="nav-links">
      <a href="#agenda" data-i18n="nav.agenda">Agenda</a>
      <a href="#speaker" data-i18n="nav.speaker">Vull ser speaker</a>
      <a href="#videos" data-i18n="nav.videos">Vídeos</a>
      <a href="#contacte" data-i18n="nav.contact">Contacte</a>
    </div>
    <div style="display:flex;align-items:center;gap:1.1rem;">
      <div class="hotel-mark"><img src="logos/termes-montbrio.webp" alt="Hotel Termes Montbrió"></div>
      <div class="lang-toggle" role="group" aria-label="Idioma">
        <button type="button" data-lang="ca" aria-pressed="true">CA</button>
        <button type="button" data-lang="es" aria-pressed="false">ES</button>
      </div>
    </div>
  </nav>
</header>

<section class="hero">
  <div class="wrap hero-grid">
    <div>
      <p class="eyebrow" data-i18n="hero.eyebrow">Hotel Termes Montbrió · Associació Cave Cavet</p>
      <h1 data-i18n="hero.title">Xerrades i tallers per pensar-hi, cada mes</h1>
      <p data-i18n="hero.body">Un espai obert de conversa, aprenentatge i comunitat entre les termes de Montbrió. La majoria de sessions són gratuïtes, amb inscripció en línia.</p>
      <div class="hero-actions">
        <a class="btn btn-brass" href="#agenda" data-i18n="hero.cta1">Veure l'agenda</a>
        <a class="btn btn-outline" href="#speaker" data-i18n="hero.cta2">Vull ser speaker</a>
      </div>
    </div>
    <div class="ticket" id="hero-ticket">
      <div class="ticket-top">
        <span class="ticket-label" data-i18n="hero.next">PRÒXIMA SESSIÓ</span>
        <span class="ticket-date mono" data-slot="date"></span>
      </div>
      <h3 data-slot="title"></h3>
      <p class="who" data-slot="who"></p>
      <a class="btn btn-ink" href="#" data-slot="cta" data-form="sesion_generica" data-i18n="hero.nextCta">Inscriu-te</a>
    </div>
  </div>
</section>

<section class="stone" id="agenda">
  <div class="wrap">
    <div class="section-head">
      <div>
        <p class="eyebrow" data-i18n="agenda.eyebrow">Programa</p>
        <h2 data-i18n="agenda.title">Pròximes sessions</h2>
      </div>
    </div>
    <div class="agenda-list" id="agenda-list"></div>
    <div class="video-empty" id="agenda-empty" hidden></div>
  </div>
</section>

<section class="cta-band" id="speaker">
  <div class="wrap">
    <p class="eyebrow" data-i18n="speaker.eyebrow">Obert a la comunitat</p>
    <h2 data-i18n="speaker.title">Tens alguna cosa a explicar?</h2>
    <p data-i18n="speaker.body">Busquem veus properes — terapeutes, investigadors, artesans, gent amb un ofici o una idea que valgui la pena compartir en 30 minuts.</p>
    <a class="btn btn-brass" href="#" data-form="speaker" data-i18n="speaker.cta">Proposa la teva xerrada</a>
  </div>
</section>

<section class="stone" id="videos">
  <div class="wrap">
    <div class="section-head">
      <div>
        <p class="eyebrow" data-i18n="videos.eyebrow">Arxiu</p>
        <h2 data-i18n="videos.title">Vídeos i pòdcast</h2>
      </div>
    </div>
    <div class="video-empty">
      <span class="eyebrow" data-i18n="videos.soon">Pròximament</span>
      <p data-i18n="videos.body">Encara no hem enregistrat cap sessió. Aquí hi apareixeran els vídeos de les xerrades i els episodis del pòdcast a mesura que es publiquin.</p>
    </div>
  </div>
</section>

<section class="newsletter">
  <div class="wrap">
    <div>
      <p class="eyebrow" data-i18n="news.eyebrow">Newsletter</p>
      <h2 data-i18n="news.title">No et perdis cap sessió</h2>
      <p data-i18n="news.body">Un correu breu, un cop al mes, amb les properes xerrades i els vídeos publicats.</p>
    </div>
    <form class="subscribe" data-form="newsletter" onsubmit="return false;">
      <input type="text" data-i18n-ph="news.name" placeholder="Nom">
      <input type="email" data-i18n-ph="news.email" placeholder="Correu electrònic">
      <button class="btn btn-brass" type="submit" data-i18n="news.cta">Subscriu-te</button>
    </form>
  </div>
</section>

<section class="stone" id="about">
  <div class="wrap about-grid">
    <div class="about-copy">
      <p class="eyebrow" data-i18n="about.eyebrow">Qui ho organitza</p>
      <h2 data-i18n="about.title">Una col·laboració entre l'hotel i l'associació</h2>
      <p data-i18n="about.body">L'Hotel Termes Montbrió posa l'espai i les termes; l'Associació Cave Cavet aporta la xarxa de speakers i la programació. Junts construïm un cicle de xerrades obert a hostes i a la comunitat local.</p>
    </div>
    <div class="logo-cards">
      <div class="logo-card">
        <img class="assoc" src="logos/cavecavet.png" alt="Associació Cave Cavet">
      </div>
      <div class="logo-card dark">
        <img src="logos/termes-montbrio.webp" alt="Hotel Termes Montbrió">
      </div>
    </div>
  </div>
</section>

<footer id="contacte">
  <div class="wrap">
    <div class="foot-grid">
      <div class="foot-brand">
        <img src="logos/cavecavet.png" alt="" style="object-fit:cover;object-position:0 0;width:30px;height:30px;">
        <span>Speakers Corner Termes Montbrió</span>
      </div>
      <div class="foot-links">
        <a href="#agenda" data-i18n="nav.agenda">Agenda</a>
        <a href="#speaker" data-i18n="nav.speaker">Vull ser speaker</a>
        <a href="mailto:associaciocavecavet@gmail.com">associaciocavecavet@gmail.com</a>
      </div>
    </div>
    <div class="foot-bottom">
      <span data-i18n="foot.orgs">Associació Cave Cavet · Hotel Termes Montbrió</span>
      <span>© 2026</span>
    </div>
  </div>
</footer>

<script src="js/i18n.js"></script>
<script src="js/app.js"></script>
</body>
</html>
```

- [ ] **Step 3: Delete the superseded mockup**

```bash
git rm preview/mockup.html
rmdir preview 2>/dev/null || true
```

- [ ] **Step 4: Manual verification (no JS yet — expected)**

Open `index.html` directly in a browser (or via the Browser pane's `navigate` on the `file://` path). Expected:
- Header, hero, agenda section (empty — no cards yet), speaker CTA, videos, newsletter, about, and footer all render with the approved dark/stone visual design.
- Browser console shows two 404s for `js/i18n.js` and `js/app.js` — expected at this point, fixed by Tasks 7–8.
- The hero ticket's date/title/who are empty (no JS populating them yet) — expected.

- [ ] **Step 5: Commit**

```bash
git add index.html css/style.css
git commit -m "feat: static page shell adapted from the approved mockup"
```

---

### Task 7: `js/i18n.js` — dictionary and language toggle

**Files:**
- Create: `js/i18n.js`

**Interfaces:**
- Produces: `window.I18N = { getLang(), setLang(lang), t(key), initI18n() }`; dispatches a `window` `CustomEvent("langchange", { detail: { lang } })` whenever the language changes.
- Consumes: `data-i18n`, `data-i18n-ph`, `.lang-toggle button[data-lang]` markup from Task 6.

- [ ] **Step 1: Write `js/i18n.js`**

```javascript
const DICT = {
  ca: {
    "nav.tag": "Termes Montbrió · Cave Cavet", "nav.agenda": "Agenda", "nav.speaker": "Vull ser speaker", "nav.videos": "Vídeos", "nav.contact": "Contacte",
    "hero.eyebrow": "Hotel Termes Montbrió · Associació Cave Cavet",
    "hero.title": "Xerrades i tallers per pensar-hi, cada mes",
    "hero.body": "Un espai obert de conversa, aprenentatge i comunitat entre les termes de Montbrió. La majoria de sessions són gratuïtes, amb inscripció en línia.",
    "hero.cta1": "Veure l'agenda", "hero.cta2": "Vull ser speaker",
    "hero.next": "PRÒXIMA SESSIÓ", "hero.nextCta": "Inscriu-te",
    "hero.emptyTitle": "La pròxima sessió es publicarà aviat.",
    "agenda.eyebrow": "Programa", "agenda.title": "Pròximes sessions", "agenda.cta": "Inscripció",
    "agenda.empty": "Pròximament noves sessions.",
    "tag.gratuito": "Gratuït",
    "speaker.eyebrow": "Obert a la comunitat", "speaker.title": "Tens alguna cosa a explicar?",
    "speaker.body": "Busquem veus properes — terapeutes, investigadors, artesans, gent amb un ofici o una idea que valgui la pena compartir en 30 minuts.",
    "speaker.cta": "Proposa la teva xerrada",
    "videos.eyebrow": "Arxiu", "videos.title": "Vídeos i pòdcast", "videos.soon": "Pròximament",
    "videos.body": "Encara no hem enregistrat cap sessió. Aquí hi apareixeran els vídeos de les xerrades i els episodis del pòdcast a mesura que es publiquin.",
    "news.eyebrow": "Newsletter", "news.title": "No et perdis cap sessió", "news.body": "Un correu breu, un cop al mes, amb les properes xerrades i els vídeos publicats.",
    "news.name": "Nom", "news.email": "Correu electrònic", "news.cta": "Subscriu-te",
    "about.eyebrow": "Qui ho organitza", "about.title": "Una col·laboració entre l'hotel i l'associació",
    "about.body": "L'Hotel Termes Montbrió posa l'espai i les termes; l'Associació Cave Cavet aporta la xarxa de speakers i la programació. Junts construïm un cicle de xerrades obert a hostes i a la comunitat local.",
    "foot.orgs": "Associació Cave Cavet · Hotel Termes Montbrió",
    "form.pending": "Formulari en preparació — s'enllaçarà properament.",
    "months": "GEN,FEB,MAR,ABR,MAI,JUN,JUL,AGO,SET,OCT,NOV,DES"
  },
  es: {
    "nav.tag": "Termes Montbrió · Cave Cavet", "nav.agenda": "Agenda", "nav.speaker": "Quiero ser speaker", "nav.videos": "Vídeos", "nav.contact": "Contacto",
    "hero.eyebrow": "Hotel Termes Montbrió · Associació Cave Cavet",
    "hero.title": "Charlas y talleres para pensar, cada mes",
    "hero.body": "Un espacio abierto de conversación, aprendizaje y comunidad en las termas de Montbrió. La mayoría de las sesiones son gratuitas, con inscripción en línea.",
    "hero.cta1": "Ver la agenda", "hero.cta2": "Quiero ser speaker",
    "hero.next": "PRÓXIMA SESIÓN", "hero.nextCta": "Inscríbete",
    "hero.emptyTitle": "La próxima sesión se publicará pronto.",
    "agenda.eyebrow": "Programa", "agenda.title": "Próximas sesiones", "agenda.cta": "Inscripción",
    "agenda.empty": "Próximamente nuevas sesiones.",
    "tag.gratuito": "Gratuito",
    "speaker.eyebrow": "Abierto a la comunidad", "speaker.title": "¿Tienes algo que contar?",
    "speaker.body": "Buscamos voces cercanas — terapeutas, investigadores, artesanos, gente con un oficio o una idea que valga la pena compartir en 30 minutos.",
    "speaker.cta": "Propón tu charla",
    "videos.eyebrow": "Archivo", "videos.title": "Vídeos y podcast", "videos.soon": "Próximamente",
    "videos.body": "Todavía no hemos grabado ninguna sesión. Aquí aparecerán los vídeos de las charlas y los episodios del podcast a medida que se publiquen.",
    "news.eyebrow": "Newsletter", "news.title": "No te pierdas ninguna sesión", "news.body": "Un correo breve, una vez al mes, con las próximas charlas y los vídeos publicados.",
    "news.name": "Nombre", "news.email": "Correo electrónico", "news.cta": "Suscríbete",
    "about.eyebrow": "Quién lo organiza", "about.title": "Una colaboración entre el hotel y la asociación",
    "about.body": "El Hotel Termes Montbrió pone el espacio y las termas; la Associació Cave Cavet aporta la red de speakers y la programación. Juntos construimos un ciclo de charlas abierto a huéspedes y a la comunidad local.",
    "foot.orgs": "Associació Cave Cavet · Hotel Termes Montbrió",
    "form.pending": "Formulario en preparación — se enlazará próximamente.",
    "months": "ENE,FEB,MAR,ABR,MAY,JUN,JUL,AGO,SEP,OCT,NOV,DIC"
  }
};

const STORAGE_KEY = "speakers-termes-lang";

function getLang() {
  return localStorage.getItem(STORAGE_KEY) || "ca";
}

function t(key) {
  return DICT[getLang()][key] || key;
}

function applyLang(lang) {
  document.documentElement.lang = lang;
  const dict = DICT[lang];
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (dict[key]) el.textContent = dict[key];
  });
  document.querySelectorAll("[data-i18n-ph]").forEach((el) => {
    const key = el.getAttribute("data-i18n-ph");
    if (dict[key]) el.setAttribute("placeholder", dict[key]);
  });
  document.querySelectorAll(".lang-toggle button").forEach((b) => {
    b.setAttribute("aria-pressed", String(b.getAttribute("data-lang") === lang));
  });
}

function setLang(lang) {
  localStorage.setItem(STORAGE_KEY, lang);
  applyLang(lang);
  window.dispatchEvent(new CustomEvent("langchange", { detail: { lang } }));
}

function initI18n() {
  applyLang(getLang());
  document.querySelectorAll(".lang-toggle button").forEach((b) => {
    b.addEventListener("click", () => setLang(b.getAttribute("data-lang")));
  });
}

window.I18N = { getLang, setLang, t, initI18n };
```

- [ ] **Step 2: Manual verification**

Serve the repo (`python3 -m http.server` from the repo root) and open `http://localhost:8000/index.html` in the Browser pane. Expected:
- All static text renders in Catalan by default.
- Clicking "ES" in the language toggle switches every static label (nav, hero, speaker CTA, videos, newsletter, about, footer) to Spanish, and the button's pressed state (visually highlighted) moves to "ES".
- Reloading the page after switching to "ES" keeps it in Spanish (persisted via `localStorage`).
- Console shows no errors (only the still-expected 404 for `js/app.js` if Task 8 isn't done yet).

- [ ] **Step 3: Commit**

```bash
git add js/i18n.js
git commit -m "feat: bilingual CA/ES dictionary and language toggle"
```

---

### Task 8: `js/app.js` — agenda rendering and form-link handling

**Files:**
- Create: `js/app.js`

**Interfaces:**
- Consumes: `window.I18N` (Task 7); `data/agenda.json` (Task 4) shaped `{ generated_at, source, sesiones: [{id, fecha, hora, titulo, ponente, lugar, tipo}] }`; DOM hooks from Task 6 (`#hero-ticket [data-slot=...]`, `#agenda-list`, `#agenda-empty`, `[data-form]`).

- [ ] **Step 1: Write `js/app.js`**

```javascript
const FORM_URLS = {
  // Reemplaça pels URLs reals de Nextcloud Forms o Google Forms quan existeixin.
  speaker: "#",
  newsletter: "#",
  sesion_generica: "#"
};

let SESSIONS = [];

function monthLabel(fecha) {
  const months = window.I18N.t("months").split(",");
  const month = parseInt(fecha.split("-")[1], 10);
  return months[month - 1];
}

function dayLabel(fecha) {
  return fecha.split("-")[2];
}

function renderHero() {
  const ticket = document.getElementById("hero-ticket");
  if (!ticket) return;
  const dateEl = ticket.querySelector('[data-slot="date"]');
  const titleEl = ticket.querySelector('[data-slot="title"]');
  const whoEl = ticket.querySelector('[data-slot="who"]');
  const ctaEl = ticket.querySelector('[data-slot="cta"]');
  const next = SESSIONS[0];

  if (!next) {
    dateEl.textContent = "";
    titleEl.textContent = window.I18N.t("hero.emptyTitle");
    whoEl.textContent = "";
    ctaEl.style.display = "none";
    return;
  }

  dateEl.textContent = `${dayLabel(next.fecha)} ${monthLabel(next.fecha)} · ${next.hora}`;
  titleEl.textContent = next.titulo;
  whoEl.textContent = next.ponente ? `${next.ponente} — ${next.lugar}` : next.lugar;
  ctaEl.style.display = "";
  ctaEl.dataset.form = "sesion_generica";
}

function renderAgenda() {
  const list = document.getElementById("agenda-list");
  const empty = document.getElementById("agenda-empty");
  if (!list || !empty) return;

  list.innerHTML = "";

  if (SESSIONS.length === 0) {
    empty.textContent = window.I18N.t("agenda.empty");
    empty.hidden = false;
    return;
  }

  empty.hidden = true;
  SESSIONS.forEach((s) => {
    const row = document.createElement("div");
    row.className = "agenda-row";

    const dateDiv = document.createElement("div");
    dateDiv.className = "agenda-date";
    dateDiv.innerHTML = `<span class="day">${dayLabel(s.fecha)}</span><span class="mon">${monthLabel(s.fecha)}</span>`;

    const infoDiv = document.createElement("div");
    const titleDiv = document.createElement("div");
    titleDiv.className = "agenda-title";
    titleDiv.textContent = s.titulo;
    const metaDiv = document.createElement("div");
    metaDiv.className = "agenda-meta";
    const tag = document.createElement("span");
    tag.className = "tag free";
    tag.textContent = window.I18N.t("tag." + s.tipo);
    const metaText = document.createElement("span");
    const parts = [s.ponente, s.hora, s.lugar].filter(Boolean);
    metaText.textContent = parts.join(" · ");
    metaDiv.appendChild(tag);
    metaDiv.appendChild(metaText);
    infoDiv.appendChild(titleDiv);
    infoDiv.appendChild(metaDiv);

    const link = document.createElement("a");
    link.className = "btn btn-outline";
    link.href = "#";
    link.dataset.form = "sesion_generica";
    link.textContent = window.I18N.t("agenda.cta");

    row.appendChild(dateDiv);
    row.appendChild(infoDiv);
    row.appendChild(link);
    list.appendChild(row);
  });

  wireFormLinks(list);
}

function wireFormLinks(scope) {
  scope.querySelectorAll("[data-form]").forEach((el) => {
    el.addEventListener("click", (event) => {
      event.preventDefault();
      const url = FORM_URLS[el.dataset.form];
      if (!url || url === "#") {
        alert(window.I18N.t("form.pending"));
        return;
      }
      window.open(url, "_blank", "noopener");
    });
  });
}

async function loadAgenda() {
  const response = await fetch("data/agenda.json", { cache: "no-store" });
  const data = await response.json();
  SESSIONS = (data.sesiones || []).slice().sort((a, b) => {
    const left = `${a.fecha}T${a.hora}`;
    const right = `${b.fecha}T${b.hora}`;
    return left.localeCompare(right);
  });
  renderHero();
  renderAgenda();
}

document.addEventListener("DOMContentLoaded", () => {
  window.I18N.initI18n();
  wireFormLinks(document);
  loadAgenda();
});

window.addEventListener("langchange", () => {
  renderHero();
  renderAgenda();
});
```

- [ ] **Step 2: Manual verification with the real (currently empty) data**

With the local server still running, reload `http://localhost:8000/index.html`. Expected (since `data/agenda.json` from Task 4 currently has `"sesiones": []`, because every real calendar event is still provisional):
- Hero ticket shows "La pròxima sessió es publicarà aviat." instead of a date/title, and its CTA button is hidden.
- Agenda section shows "Pròximament noves sessions." instead of an empty list.
- No console errors.
- Clicking the "Vull ser speaker" or newsletter "Subscriu-te" buttons shows the "Formulari en preparació…" alert.

- [ ] **Step 3: Commit**

```bash
git add js/app.js
git commit -m "feat: render agenda from data/agenda.json and wire form-link placeholders"
```

---

### Task 9: End-to-end verification with populated agenda data

**Files:**
- Temporary (not committed): a scratch copy of `data/agenda.json` with sample sessions.
- No repo files change in this task beyond what's already committed.

**Interfaces:**
- Consumes: everything from Tasks 6–8.

- [ ] **Step 1: Back up the real (empty) agenda file**

```bash
cp data/agenda.json /tmp/agenda-real-backup.json
```

- [ ] **Step 2: Write a temporary populated fixture over `data/agenda.json`**

```json
{
  "generated_at": "2026-09-11T15:00:00Z",
  "source": "https://cloud.cavecavet.org/remote.php/dav/public-calendars/RP5xH59a33ZBNwLx?export",
  "sesiones": [
    {
      "id": "evt-1",
      "fecha": "2026-10-15",
      "hora": "19:00",
      "titulo": "El silenci com a eina de benestar",
      "ponente": "Mercè Milán",
      "lugar": "Hotel Termes de Montbrió",
      "tipo": "gratuito"
    },
    {
      "id": "evt-2",
      "fecha": "2026-11-05",
      "hora": "11:00",
      "titulo": "Filosofia de sobretaula: aprendre a no tenir raó",
      "ponente": "Dr. Adrià Puig",
      "lugar": "Hotel Termes de Montbrió",
      "tipo": "gratuito"
    }
  ]
}
```

- [ ] **Step 3: Verify populated rendering in the browser**

Reload `http://localhost:8000/index.html`. Expected:
- Hero ticket shows "15 OCT · 19:00", title "El silenci com a eina de benestar", and "Mercè Milán — Hotel Termes de Montbrió".
- Agenda list shows both sessions as rows, ordered earliest first, each with a "Gratuït" tag and an "Inscripció" button.
- Clicking "ES" switches "Gratuït"→"Gratuito" and "Inscripció"→"Inscripción" on both cards immediately (no reload), while the session titles/speaker names stay unchanged (they're not bilingual, per spec).
- Clicking an "Inscripció"/"Inscripción" button shows the "Formulari en preparació…" alert.

- [ ] **Step 4: Check responsiveness**

Using the Browser pane's `resize_window` with `preset: "mobile"`, reload the page. Expected: nav links collapse (already handled by existing `@media (max-width:760px)` rule), hero and agenda grids stack to a single column, agenda row's inscription button moves below the title. Reset with `resize_window` `preset: "desktop"` afterward.

- [ ] **Step 5: Restore the real agenda file**

```bash
cp /tmp/agenda-real-backup.json data/agenda.json
git status
```
Expected: `git status` shows no changes to `data/agenda.json` (it's back to what Task 4 committed) — nothing to commit for this task.

---

### Task 10: Publish — GitHub repo, Pages, and DNS

**⚠ Requires explicit user confirmation before Step 2 (creates a public GitHub repo and pushes) and before Step 4 (changes live DNS-adjacent GitHub Pages settings).** Do not run those steps without the user explicitly saying to proceed at execution time — a prior approval of this plan is not itself that confirmation.

**Files:** none (infrastructure/publishing only).

- [ ] **Step 1: Review what will be pushed**

```bash
cd ~/Documents/GitHub/speakers-termes-montbrio
git log --oneline
git status
```
Confirm there are no uncommitted changes and the commit history matches Tasks 1–8.

- [ ] **Step 2: Confirm with the user, then create the GitHub repo and push**

Ask the user to confirm the org/visibility, then:
```bash
gh repo create cavecavet/speakers-termes-montbrio --public --source=. --remote=origin
git push -u origin main
```

- [ ] **Step 3: Verify the push**

```bash
gh repo view cavecavet/speakers-termes-montbrio --web
```
Expected: repository visible on GitHub with all committed files, including `.github/workflows/sync-agenda.yml`.

- [ ] **Step 4: Confirm with the user, then enable GitHub Pages**

```bash
gh api repos/cavecavet/speakers-termes-montbrio/pages -X POST -f "source[branch]=main" -f "source[path]=/"
```
If this fails because Pages is already configured differently, guide the user to Settings → Pages in the GitHub web UI instead.

- [ ] **Step 5: Tell the user the remaining manual step (DNS)**

Report to the user: they need to add a `CNAME` DNS record for `speakers.cavecavet.org` pointing to `cavecavet.github.io`, at whichever provider hosts the `cavecavet.org` zone (same place `espigo.cavecavet.org` was configured) — this is outside what any tool available here can do.

- [ ] **Step 6: Verify the workflow runs**

```bash
gh workflow run sync-agenda.yml --repo cavecavet/speakers-termes-montbrio
gh run list --repo cavecavet/speakers-termes-montbrio --limit 1
```
Expected: a run appears and completes successfully (green).
