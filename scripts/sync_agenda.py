"""Sync data/agenda.json from the public Nextcloud Calendar export."""

import base64
import json
import os
import smtplib
import sys
import urllib.request
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from zoneinfo import ZoneInfo

from icalendar import Calendar

ICS_URL = "https://cloud.cavecavet.org/remote.php/dav/public-calendars/RP5xH59a33ZBNwLx?export"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "agenda.json"

NEXTCLOUD_BASE = "https://cloud.cavecavet.org"
NEXTCLOUD_USER = "admin"
# Cloudflare (fronting cloud.cavecavet.org) returns 403 to urllib's default
# "Python-urllib/x.y" User-Agent on every endpoint, not just the calendar
# export -- a normal browser-like one passes through everywhere.
USER_AGENT = "Mozilla/5.0"
# "Confirmar asistencia — [Evento] · Speaker's Corner" — cloned per newly
# confirmed session instead of recreated from scratch, so any future tweak to
# its questions only has to happen once, in Nextcloud.
TEMPLATE_FORM_ID = 3
ADMINS_GROUP = "admins"
MAX_SUBMISSIONS = 140
EMAIL_QUESTION_TEXT = "Correo electrónico"

# Same outgoing mail server already configured in Nextcloud (Ajustes básicos ->
# Servidor de correo electrónico) -- only the password is a secret.
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465
SMTP_USER = "associaciocavecavet@gmail.com"
SMTP_FROM = "associaciocavecavet@gmail.com"


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
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
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
    request.add_header("User-Agent", USER_AGENT)
    request.add_header("OCS-APIRequest", "true")
    request.add_header("Accept", "application/json")
    if data is not None:
        request.add_header("Content-Type", "application/json")
    token = base64.b64encode(f"{NEXTCLOUD_USER}:{app_password}".encode("utf-8")).decode("ascii")
    request.add_header("Authorization", f"Basic {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload["ocs"]["data"]


def ensure_attendance_form(session: dict, app_password: str) -> tuple[int, str]:
    """Clone the template attendance form for `session` and return
    `(form_id, public_submission_url)` — closed at 140 responses or the talk's
    start time, whichever comes first, with the "admins" group able to see
    who signed up.
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
    return form_id, f"{NEXTCLOUD_BASE}/apps/forms/s/{link_share['shareWith']}"


def attach_form_urls(sessions: list[dict], old_by_id: dict, app_password: str | None) -> None:
    """Give every session a `form_id`/`form_url`, mutating each dict in place.

    Reuses a session's existing form when carried over from the previous run
    (never creates a second form for the same session id). Otherwise creates a
    new attendance form via the Nextcloud Forms API — skipped entirely when
    `app_password` is falsy (e.g. local runs without the
    NEXTCLOUD_APP_PASSWORD secret). A per-session failure is logged and leaves
    that session's form_url as None (the site falls back to its "pending"
    message) rather than aborting the whole sync.
    """
    for session in sessions:
        existing = old_by_id.get(session["id"])
        if existing and existing.get("form_url"):
            session["form_url"] = existing["form_url"]
            session["form_id"] = existing.get("form_id")
            continue
        session["form_url"] = None
        session["form_id"] = None
        if not app_password:
            continue
        try:
            form_id, url = ensure_attendance_form(session, app_password)
            session["form_id"] = form_id
            session["form_url"] = url
        except Exception as error:
            print(f"No s'ha pogut crear el formulari d'assistència per a {session['id']}: {error}")


def find_email_question_id(questions: list[dict]) -> int | None:
    for question in questions:
        if question.get("text") == EMAIL_QUESTION_TEXT:
            return question["id"]
    return None


def fetch_submission_emails(form_id: int, app_password: str) -> list[str]:
    """Return every respondent's email address already recorded on the form."""
    data = nc_request("GET", f"/forms/{form_id}/submissions", app_password)
    email_question_id = find_email_question_id(data.get("questions", []))
    if email_question_id is None:
        return []
    emails = []
    for submission in data.get("submissions", []):
        for answer in submission.get("answers", []):
            if answer.get("questionId") == email_question_id and answer.get("text"):
                emails.append(answer["text"])
    return emails


def send_email(to_addrs: list[str], subject: str, body: str, smtp_password: str) -> None:
    """Send one email, addressed to ourselves with every respondent in Bcc so
    strangers who filled in a public form never see each other's address."""
    if not to_addrs:
        return
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = SMTP_FROM
    message["To"] = SMTP_FROM
    message["Bcc"] = ", ".join(to_addrs)
    message.set_content(body)
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30) as smtp:
        smtp.login(SMTP_USER, smtp_password)
        smtp.send_message(message)


def build_date_change_email(session: dict, old_session: dict) -> tuple[str, str]:
    subject = f"Cambio de fecha: {session['titulo']}"
    body = (
        "Hola,\n\n"
        f"La sesión «{session['titulo']}» del Speaker's Corner ha cambiado de fecha.\n\n"
        f"Antes: {format_session_datetime(old_session['fecha'], old_session['hora'])}\n"
        f"Ahora: {format_session_datetime(session['fecha'], session['hora'])}\n"
        f"Lugar: {session['lugar']}\n\n"
        "Tu inscripción se mantiene, no hace falta que vuelvas a apuntarte. Si la "
        f"nueva fecha no te va bien, escríbenos a {SMTP_FROM}.\n\n"
        "Gracias,\nSpeaker's Corner Termes Montbrió"
    )
    return subject, body


def build_cancellation_email(old_session: dict) -> tuple[str, str]:
    subject = f"Sesión cancelada: {old_session['titulo']}"
    body = (
        "Hola,\n\n"
        f"Lamentamos informarte de que la sesión «{old_session['titulo']}», prevista "
        f"para el {format_session_datetime(old_session['fecha'], old_session['hora'])}, ha "
        "sido cancelada.\n\n"
        f"Disculpa las molestias. Si tienes alguna duda, escríbenos a {SMTP_FROM}.\n\n"
        "Gracias,\nSpeaker's Corner Termes Montbrió"
    )
    return subject, body


def handle_date_change(
    session: dict, old_session: dict, app_password: str, smtp_password: str | None
) -> None:
    form_id = session.get("form_id")
    if not form_id:
        return
    try:
        nc_request(
            "PATCH",
            f"/forms/{form_id}",
            app_password,
            {
                "keyValuePairs": {
                    "title": build_form_title(session),
                    "description": build_form_description(session),
                    "expires": session_expiry_timestamp(session["fecha"], session["hora"]),
                }
            },
        )
        if smtp_password:
            emails = fetch_submission_emails(form_id, app_password)
            if emails:
                subject, body = build_date_change_email(session, old_session)
                send_email(emails, subject, body, smtp_password)
    except Exception as error:
        print(f"No s'ha pogut actualitzar/avisar del canvi de data per a {session['id']}: {error}")


def handle_cancellation(old_session: dict, app_password: str, smtp_password: str | None) -> None:
    form_id = old_session.get("form_id")
    if not form_id:
        return
    try:
        nc_request("PATCH", f"/forms/{form_id}", app_password, {"keyValuePairs": {"state": 1}})
        if smtp_password:
            emails = fetch_submission_emails(form_id, app_password)
            if emails:
                subject, body = build_cancellation_email(old_session)
                send_email(emails, subject, body, smtp_password)
    except Exception as error:
        print(
            "No s'ha pogut tancar el formulari / avisar de la cancel·lació per a "
            f"{old_session['id']}: {error}"
        )


def sync_changes_and_cancellations(
    new_sessions: list[dict],
    old_by_id: dict,
    today: str,
    app_password: str | None,
    smtp_password: str | None,
) -> None:
    """Detect date changes and cancellations against the previous run and act
    on them — skipped entirely without an app password (nothing to call).

    A session that simply aged into the past (its own `fecha` is now before
    `today`) is not a cancellation — parse_sessions drops it on purpose, same
    as any other past session. Only a still-upcoming session that vanished
    (deleted, or un-confirmed) counts as cancelled.
    """
    if not app_password:
        return
    new_by_id = {s["id"]: s for s in new_sessions}
    for session in new_sessions:
        old = old_by_id.get(session["id"])
        if not old or not old.get("form_id"):
            continue
        if old["fecha"] != session["fecha"] or old["hora"] != session["hora"]:
            handle_date_change(session, old, app_password, smtp_password)
    for old_id, old_session in old_by_id.items():
        if old_id in new_by_id or not old_session.get("form_id"):
            continue
        if old_session["fecha"] < today:
            continue  # aged into the past on its own -- not a cancellation
        handle_cancellation(old_session, app_password, smtp_password)


def main() -> int:
    ics_bytes = fetch_ics(ICS_URL)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    agenda = build_agenda(ics_bytes, ICS_URL, generated_at, today=today)
    new_sessions = agenda["sesiones"]

    old_sessions = None
    if OUTPUT_PATH.exists():
        try:
            old_sessions = json.loads(OUTPUT_PATH.read_text(encoding="utf-8")).get("sesiones")
        except json.JSONDecodeError:
            old_sessions = None

    old_by_id = {s["id"]: s for s in (old_sessions or [])}
    app_password = os.environ.get("NEXTCLOUD_APP_PASSWORD")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    sync_changes_and_cancellations(new_sessions, old_by_id, today, app_password, smtp_password)
    attach_form_urls(new_sessions, old_by_id, app_password)

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
