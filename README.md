# Speaker's Corner Termes Montbrió

Lloc estàtic (sense build) del cicle de xerrades organitzat per l'Associació Cave
Cavet i l'Hotel Termes Montbrió. Publicat a `speakers.cavecavet.org` via GitHub
Pages.

- Disseny i decisions: `docs/superpowers/specs/2026-09-11-speakers-termes-montbrio-design.md`
- L'agenda (`data/agenda.json`) es genera automàticament — **no s'edita a mà**. La
  font és el calendari Nextcloud `Xerrades Hotel Termes Montbrió`
  (`https://cloud.cavecavet.org/apps/calendar/p/RP5xH59a33ZBNwLx`).

## Com afegir una sessió al lloc

Al calendari Nextcloud, per a cada xerrada:

1. Crea l'esdeveniment amb la data i l'hora reals.
2. **Marca'l com a Confirmat** (no «Tentatiu»/«provisional») — el lloc **només**
   mostra esdeveniments confirmats; els provisionals queden invisibles fins que
   els confirmis.
3. A la descripció, escriu-hi exactament aquest format (dues línies, en aquest
   ordre — el sincronitzador el busca literalment):
   ```
   Ponent: <nom del ponent>
   Tema: <títol de la xerrada>
   ```
   Si no segueixes aquest format, el lloc mostrarà la descripció sencera com a
   títol i deixarà el ponent en blanc.
4. Deixa passar fins a 4 hores (el cron de GitHub Actions sincronitza cada 4h), o
   força-ho ara mateix des de la pestanya **Actions** del repo → workflow
   *«Sync agenda from Nextcloud Calendar»* → **Run workflow**.

Les sessions amb data anterior a avui desapareixen soles de l'agenda (no cal
esborrar-les del calendari).

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
- Formularis (inscripció/newsletter): encara no creats. Plantilla de preguntes a
  `docs/formularis-plantilla.md` — un cop creats a Nextcloud Forms o Google Forms,
  enganxa'n l'URL a `FORM_URLS` dins `js/app.js`.
- **Pendent:** el registre DNS CNAME de `speakers.cavecavet.org` cap a
  `cavecavet.github.io` encara s'ha d'afegir on es gestioni el domini
  `cavecavet.org`; fins que no existeixi, el lloc només és accessible a
  `https://cavecavet.github.io/speakers-termes-montbrio/`.
