"""Sync data/agenda.json from the public Nextcloud Calendar export."""

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from icalendar import Calendar

ICS_URL = "https://cloud.cavecavet.org/remote.php/dav/public-calendars/RP5xH59a33ZBNwLx?export"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "agenda.json"


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


def parse_sessions(ics_bytes: bytes, today: str | None = None) -> list[dict]:
    """Parse calendar bytes into CONFIRMED, non-past sessions, sorted by fecha+hora.

    A session is dropped once its `fecha` is strictly before `today`
    (`YYYY-MM-DD`, defaults to the current UTC date) — same-day sessions stay
    visible until midnight rather than disappearing during the day they happen.
    """
    if today is None:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    calendar = Calendar.from_ical(ics_bytes)
    sessions = []
    for component in calendar.walk("VEVENT"):
        status = str(component.get("status", "")).upper()
        if status != "CONFIRMED":
            continue
        dtstart_prop = component.get("dtstart")
        if dtstart_prop is None:
            continue
        dtstart = dtstart_prop.dt
        fecha = dtstart.strftime("%Y-%m-%d")
        if fecha < today:
            continue
        titulo, ponente = parse_description(str(component.get("description", "")))
        sessions.append(
            {
                "id": str(component.get("uid", "")),
                "fecha": fecha,
                "hora": dtstart.strftime("%H:%M"),
                "titulo": titulo,
                "ponente": ponente,
                "lugar": str(component.get("location", "")),
                "tipo": "gratuito",
            }
        )
    sessions.sort(key=lambda s: (s["fecha"], s["hora"]))
    return sessions


def build_agenda(ics_bytes: bytes, source_url: str, generated_at: str) -> dict:
    return {
        "generated_at": generated_at,
        "source": source_url,
        "sesiones": parse_sessions(ics_bytes),
    }


def fetch_ics(url: str) -> bytes:
    # Cloudflare (fronting cloud.cavecavet.org) returns 403 to urllib's default
    # "Python-urllib/x.y" User-Agent; a normal browser-like one passes through.
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
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
