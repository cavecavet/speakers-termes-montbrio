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
