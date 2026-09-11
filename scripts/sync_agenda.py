"""Sync data/agenda.json from the public Nextcloud Calendar export."""

from icalendar import Calendar


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


def parse_sessions(ics_bytes: bytes) -> list[dict]:
    """Parse calendar bytes into CONFIRMED sessions, sorted by fecha+hora."""
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
