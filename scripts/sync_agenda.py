"""Sync data/agenda.json from the public Nextcloud Calendar export."""

import base64
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from icalendar import Calendar

ICS_URL = "https://cloud.cavecavet.org/remote.php/dav/public-calendars/RP5xH59a33ZBNwLx?export"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "agenda.json"

NEXTCLOUD_BASE = "https://cloud.cavecavet.org"
NEXTCLOUD_USER = "admin"
# "Confirmar asistencia — [Evento] · Speaker's Corner" — cloned per newly
# confirmed session instead of recreated from scratch, so any future tweak to
# its questions only has to happen once, in Nextcloud.
TEMPLATE_FORM_ID = 3
ADMINS_GROUP = "admins"
MAX_SUBMISSIONS = 140


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


def build_agenda(
    ics_bytes: bytes, source_url: str, generated_at: str, today: str | None = None
) -> dict:
    return {
        "generated_at": generated_at,
        "source": source_url,
        "sesiones": parse_sessions(ics_bytes, today=today),
    }


def fetch_ics(url: str) -> bytes:
    # Cloudflare (fronting cloud.cavecavet.org) returns 403 to urllib's default
    # "Python-urllib/x.y" User-Agent; a normal browser-like one passes through.
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def format_session_datetime(fecha: str, hora: str) -> str:
    dt = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
    return dt.strftime("%d/%m/%Y · %H:%M")


def session_price_label(tipo: str) -> str:
    return "Gratuïta" if tipo == "gratuito" else tipo


def session_expiry_timestamp(fecha: str, hora: str) -> int:
    """Unix timestamp of the session's exact start time in Europe/Madrid.

    Used as the attendance form's `expires` — registration closes the moment
    the talk begins, not at the end of that calendar day.
    """
    dt = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M").replace(
        tzinfo=ZoneInfo("Europe/Madrid")
    )
    return int(dt.timestamp())


def build_form_title(session: dict) -> str:
    who = session["ponente"] or session["titulo"]
    return f"Confirmar asistencia — Speaker's Corner · {who}"


def build_form_description(session: dict) -> str:
    return (
        "Confirma tu asistencia a esta sesión del Speaker's Corner.\n\n"
        f"**Evento:** {session['titulo']}\n"
        f"**Ponente:** {session['ponente'] or '—'}\n"
        f"**Fecha:** {format_session_datetime(session['fecha'], session['hora'])}\n"
        f"**Lugar:** {session['lugar']}\n"
        f"**Precio:** {session_price_label(session['tipo'])}\n\n"
        "Plazas limitadas. Rellena este formulario para reservar tu plaza."
    )


def nc_request(method: str, path: str, app_password: str, body: dict | None = None) -> dict:
    """Call the Nextcloud Forms OCS API (v3) at `path`, authenticated as admin."""
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(
        f"{NEXTCLOUD_BASE}/ocs/v2.php/apps/forms/api/v3{path}", data=data, method=method
    )
    request.add_header("OCS-APIRequest", "true")
    request.add_header("Accept", "application/json")
    if data is not None:
        request.add_header("Content-Type", "application/json")
    token = base64.b64encode(f"{NEXTCLOUD_USER}:{app_password}".encode("utf-8")).decode("ascii")
    request.add_header("Authorization", f"Basic {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload["ocs"]["data"]


def ensure_attendance_form(session: dict, app_password: str) -> str:
    """Clone the template attendance form for `session` and return its public
    submission URL — closed at 140 responses or the talk's start time,
    whichever comes first, with the "admins" group able to see who signed up.
    """
    cloned = nc_request("POST", f"/forms?fromId={TEMPLATE_FORM_ID}", app_password)
    form_id = cloned["id"]
    nc_request(
        "PATCH",
        f"/forms/{form_id}",
        app_password,
        {
            "keyValuePairs": {
                "title": build_form_title(session),
                "description": build_form_description(session),
                "expires": session_expiry_timestamp(session["fecha"], session["hora"]),
                "maxSubmissions": MAX_SUBMISSIONS,
            }
        },
    )
    link_share = nc_request(
        "POST",
        f"/forms/{form_id}/shares",
        app_password,
        {"shareType": 3, "permissions": ["submit"]},
    )
    nc_request(
        "POST",
        f"/forms/{form_id}/shares",
        app_password,
        {"shareType": 1, "shareWith": ADMINS_GROUP, "permissions": ["submit", "results"]},
    )
    return f"{NEXTCLOUD_BASE}/apps/forms/s/{link_share['shareWith']}"


def attach_form_urls(sessions: list[dict], old_by_id: dict, app_password: str | None) -> None:
    """Give every session a `form_url`, mutating each dict in place.

    Reuses a session's existing form_url when carried over from the previous
    run (never creates a second form for the same session id). Otherwise
    creates a new attendance form via the Nextcloud Forms API — skipped
    entirely when `app_password` is falsy (e.g. local runs without the
    NEXTCLOUD_APP_PASSWORD secret). A per-session failure is logged and leaves
    that session's form_url as None (the site falls back to its "pending"
    message) rather than aborting the whole sync.
    """
    for session in sessions:
        existing = old_by_id.get(session["id"])
        if existing and existing.get("form_url"):
            session["form_url"] = existing["form_url"]
            continue
        session["form_url"] = None
        if not app_password:
            continue
        try:
            session["form_url"] = ensure_attendance_form(session, app_password)
        except Exception as error:
            print(f"No s'ha pogut crear el formulari d'assistència per a {session['id']}: {error}")


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

    old_by_id = {s["id"]: s for s in (old_sessions or [])}
    attach_form_urls(new_sessions, old_by_id, os.environ.get("NEXTCLOUD_APP_PASSWORD"))

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
