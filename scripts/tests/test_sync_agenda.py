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
