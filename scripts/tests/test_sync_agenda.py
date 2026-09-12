import json
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
    sessions = parse_sessions(ics_bytes, today="2026-10-15")
    assert len(sessions) == 1
    assert sessions[0]["id"] == "evt-confirmed-1@cavecavet.org"


def test_parse_sessions_excludes_confirmed_events_before_today():
    # CONFIRMED_EVENT is 2026-10-15; "today" here is after it, so it must drop out.
    ics_bytes = make_ics(CONFIRMED_EVENT)
    sessions = parse_sessions(ics_bytes, today="2026-10-16")
    assert sessions == []


def test_parse_sessions_keeps_confirmed_event_dated_today():
    # Same-day sessions stay visible until midnight, not just up to their start time.
    ics_bytes = make_ics(CONFIRMED_EVENT)
    sessions = parse_sessions(ics_bytes, today="2026-10-15")
    assert [s["id"] for s in sessions] == ["evt-confirmed-1@cavecavet.org"]


def test_parse_sessions_maps_fields_correctly():
    ics_bytes = make_ics(CONFIRMED_EVENT)
    session = parse_sessions(ics_bytes, today="2026-10-15")[0]
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
    session = parse_sessions(ics_bytes, today="2026-10-05")[0]
    assert session["titulo"] == "Xerrada oberta sobre gestió del temps, sense format estàndard."
    assert session["ponente"] == ""


def test_parse_sessions_sorts_by_date_then_time():
    ics_bytes = make_ics(CONFIRMED_EVENT, CONFIRMED_NO_PATTERN_EVENT)
    sessions = parse_sessions(ics_bytes, today="2026-10-05")
    assert [s["id"] for s in sessions] == [
        "evt-confirmed-2@cavecavet.org",
        "evt-confirmed-1@cavecavet.org",
    ]


def test_parse_sessions_returns_empty_list_when_nothing_confirmed():
    ics_bytes = make_ics(TENTATIVE_EVENT)
    assert parse_sessions(ics_bytes) == []


CONFIRMED_NO_DTSTART_EVENT = """BEGIN:VEVENT
UID:evt-confirmed-malformed@cavecavet.org
DTSTAMP:20260901T090000Z
SUMMARY:Speakers' Corner · esdeveniment mal format
LOCATION:Hotel Termes de Montbrió
DESCRIPTION:Ponent: Algú\\nTema: Sense data d'inici
STATUS:CONFIRMED
END:VEVENT
"""


def test_parse_sessions_skips_confirmed_event_without_dtstart():
    ics_bytes = make_ics(CONFIRMED_NO_DTSTART_EVENT, CONFIRMED_EVENT)
    sessions = parse_sessions(ics_bytes, today="2026-10-15")
    assert [s["id"] for s in sessions] == ["evt-confirmed-1@cavecavet.org"]


from sync_agenda import build_agenda


def test_build_agenda_wraps_sessions_with_metadata():
    ics_bytes = make_ics(CONFIRMED_EVENT)
    agenda = build_agenda(
        ics_bytes, "https://example.org/feed.ics", "2026-09-11T15:00:00Z", today="2026-10-15"
    )
    assert agenda["source"] == "https://example.org/feed.ics"
    assert agenda["generated_at"] == "2026-09-11T15:00:00Z"
    assert len(agenda["sesiones"]) == 1
    assert agenda["sesiones"][0]["id"] == "evt-confirmed-1@cavecavet.org"


from sync_agenda import (
    build_form_description,
    build_form_title,
    format_session_datetime,
    session_expiry_timestamp,
    session_price_label,
)

SAMPLE_SESSION = {
    "id": "evt-1",
    "fecha": "2026-10-02",
    "hora": "17:00",
    "titulo": "Beneficis de l'aigua i del mar per a la salut i el sistema nerviós",
    "ponente": "Mercè Milán",
    "lugar": "Hotel Termes de Montbrió",
    "tipo": "gratuito",
}


def test_format_session_datetime():
    assert format_session_datetime("2026-10-02", "17:00") == "02/10/2026 · 17:00"


def test_session_price_label_gratuito():
    assert session_price_label("gratuito") == "Gratuïta"


def test_session_price_label_falls_back_to_raw_value_for_unknown_types():
    assert session_price_label("15€") == "15€"


def test_build_form_title_uses_speaker_name():
    assert build_form_title(SAMPLE_SESSION) == "Confirmar asistencia — Speaker's Corner · Mercè Milán"


def test_build_form_title_falls_back_to_event_title_without_a_speaker():
    session = {**SAMPLE_SESSION, "ponente": ""}
    assert (
        build_form_title(session)
        == "Confirmar asistencia — Speaker's Corner · "
        "Beneficis de l'aigua i del mar per a la salut i el sistema nerviós"
    )


def test_build_form_description_fills_in_the_template_placeholders():
    description = build_form_description(SAMPLE_SESSION)
    assert "**Evento:** Beneficis de l'aigua i del mar per a la salut i el sistema nerviós" in description
    assert "**Ponente:** Mercè Milán" in description
    assert "**Fecha:** 02/10/2026 · 17:00" in description
    assert "**Lugar:** Hotel Termes de Montbrió" in description
    assert "**Precio:** Gratuïta" in description


def test_build_form_description_shows_a_dash_when_speaker_is_missing():
    session = {**SAMPLE_SESSION, "ponente": ""}
    assert "**Ponente:** —" in build_form_description(session)


def test_session_expiry_timestamp_matches_europe_madrid_start_time():
    # 2026-10-02 17:00 Europe/Madrid (CEST, UTC+2) == 15:00 UTC == 1790953200.
    assert session_expiry_timestamp("2026-10-02", "17:00") == 1790953200


import sync_agenda
from sync_agenda import attach_form_urls


def test_attach_form_urls_carries_over_an_existing_url_without_calling_the_api(monkeypatch):
    called = False

    def fake_ensure(session, app_password):
        nonlocal called
        called = True
        return "https://should-not-be-called"

    monkeypatch.setattr(sync_agenda, "ensure_attendance_form", fake_ensure)

    sessions = [{**SAMPLE_SESSION, "form_url": None}]
    old_by_id = {"evt-1": {**SAMPLE_SESSION, "form_url": "https://cloud.cavecavet.org/apps/forms/s/existing"}}

    attach_form_urls(sessions, old_by_id, app_password="dummy")

    assert sessions[0]["form_url"] == "https://cloud.cavecavet.org/apps/forms/s/existing"
    assert called is False


def test_attach_form_urls_creates_a_form_for_a_session_without_one(monkeypatch):
    calls = []

    def fake_ensure(session, app_password):
        calls.append((session["id"], app_password))
        return "https://cloud.cavecavet.org/apps/forms/s/brand-new"

    monkeypatch.setattr(sync_agenda, "ensure_attendance_form", fake_ensure)

    sessions = [dict(SAMPLE_SESSION)]
    attach_form_urls(sessions, old_by_id={}, app_password="secret123")

    assert sessions[0]["form_url"] == "https://cloud.cavecavet.org/apps/forms/s/brand-new"
    assert calls == [("evt-1", "secret123")]


def test_attach_form_urls_skips_creation_without_an_app_password(monkeypatch):
    def fake_ensure(session, app_password):
        raise AssertionError("should never be called without an app password")

    monkeypatch.setattr(sync_agenda, "ensure_attendance_form", fake_ensure)

    sessions = [dict(SAMPLE_SESSION)]
    attach_form_urls(sessions, old_by_id={}, app_password=None)

    assert sessions[0]["form_url"] is None


def test_attach_form_urls_logs_and_continues_when_creation_fails(monkeypatch, capsys):
    def failing_ensure(session, app_password):
        raise RuntimeError("Nextcloud is down")

    monkeypatch.setattr(sync_agenda, "ensure_attendance_form", failing_ensure)

    sessions = [dict(SAMPLE_SESSION)]
    attach_form_urls(sessions, old_by_id={}, app_password="secret123")

    assert sessions[0]["form_url"] is None
    assert "Nextcloud is down" in capsys.readouterr().out


from sync_agenda import ensure_attendance_form


class FakeResponse:
    def __init__(self, payload):
        self._body = json.dumps({"ocs": {"data": payload}}).encode("utf-8")

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_ensure_attendance_form_clones_configures_and_shares_in_order(monkeypatch):
    responses = [
        {"id": 42},  # clone
        42,  # patch (form id echoed back)
        {"id": 1, "shareType": 3, "shareWith": "pub1234567890ab"},  # public link share
        {"id": 2, "shareType": 1, "shareWith": "admins"},  # admins group share
    ]
    calls = []

    def fake_urlopen(request, timeout=30):
        calls.append(
            {
                "url": request.full_url,
                "method": request.get_method(),
                "body": json.loads(request.data) if request.data else None,
                "auth": request.get_header("Authorization"),
            }
        )
        return FakeResponse(responses[len(calls) - 1])

    monkeypatch.setattr(sync_agenda.urllib.request, "urlopen", fake_urlopen)

    url = ensure_attendance_form(SAMPLE_SESSION, app_password="s3cr3t")

    assert url == "https://cloud.cavecavet.org/apps/forms/s/pub1234567890ab"
    assert len(calls) == 4

    clone_call, patch_call, link_share_call, group_share_call = calls

    assert clone_call["method"] == "POST"
    assert clone_call["url"].endswith("/forms?fromId=3")
    assert clone_call["auth"].startswith("Basic ")

    assert patch_call["method"] == "PATCH"
    assert patch_call["url"].endswith("/forms/42")
    kv = patch_call["body"]["keyValuePairs"]
    assert kv["title"] == "Confirmar asistencia — Speaker's Corner · Mercè Milán"
    assert kv["expires"] == 1790953200
    assert kv["maxSubmissions"] == 140

    assert link_share_call["method"] == "POST"
    assert link_share_call["url"].endswith("/forms/42/shares")
    assert link_share_call["body"] == {"shareType": 3, "permissions": ["submit"]}

    assert group_share_call["method"] == "POST"
    assert group_share_call["url"].endswith("/forms/42/shares")
    assert group_share_call["body"] == {
        "shareType": 1,
        "shareWith": "admins",
        "permissions": ["submit", "results"],
    }
