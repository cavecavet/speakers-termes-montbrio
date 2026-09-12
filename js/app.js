const FORM_URLS = {
  // Reemplaça pels URLs reals de Nextcloud Forms o Google Forms quan existeixin.
  speaker: "https://cloud.cavecavet.org/apps/forms/s/2LJptgTKoXNtGRTKfEZMqcjT",
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
  if (next.form_url) {
    ctaEl.dataset.url = next.form_url;
  } else {
    delete ctaEl.dataset.url;
  }
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
    if (s.form_url) {
      link.dataset.url = s.form_url;
    }
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
      const url = el.dataset.url || FORM_URLS[el.dataset.form];
      if (!url || url === "#") {
        alert(window.I18N.t("form.pending"));
        return;
      }
      window.open(url, "_blank", "noopener");
    });
  });
}

async function loadAgenda() {
  try {
    const response = await fetch("data/agenda.json", { cache: "no-store" });
    const data = await response.json();
    SESSIONS = (data.sesiones || []).slice().sort((a, b) => {
      const left = `${a.fecha}T${a.hora}`;
      const right = `${b.fecha}T${b.hora}`;
      return left.localeCompare(right);
    });
  } catch (error) {
    // data/agenda.json missing or malformed (e.g. local dev before the sync
    // script has ever run): degrade to the designed empty state instead of
    // leaving the hero ticket half-populated and the agenda section blank.
    console.error("No s'ha pogut carregar data/agenda.json:", error);
    SESSIONS = [];
  }
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
