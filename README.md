# Speaker's Corner Termes Montbrió

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
