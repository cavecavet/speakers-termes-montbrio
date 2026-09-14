const DICT = {
  ca: {
    "nav.tag": "Associació Cave Cavet", "nav.agenda": "Agenda", "nav.speaker": "Vull ser speaker", "nav.videos": "Vídeos", "nav.contact": "Contacte",
    "hero.eyebrow": "Associació Cave Cavet, xerrades\nA l'Hotel Termes Montbrió",
    "hero.title": "Xerrades i tallers per pensar-hi, cada mes",
    "hero.body": "Un espai obert de conversa, aprenentatge i comunitat a les termes de Montbrió. Sessions gratuïtes, amb inscripció en línia.",
    "hero.cta1": "Veure l'agenda", "hero.cta2": "Vull ser speaker",
    "hero.next": "PROPERA SESSIÓ", "hero.nextCta": "Inscriu-te",
    "hero.emptyTitle": "La pròxima sessió es publicarà aviat.",
    "agenda.eyebrow": "Programa", "agenda.title": "Properes sessions", "agenda.cta": "Inscripció",
    "agenda.empty": "Pròximament noves sessions.",
    "tag.gratuito": "Gratuït",
    "speaker.eyebrow": "Obert a la comunitat", "speaker.title": "Tens alguna cosa a explicar?",
    "speaker.body": "Busquem veus properes — terapeutes, investigadors, artesans, gent amb un ofici o una idea que valgui la pena compartir en 30 minuts.",
    "speaker.cta": "Proposa la teva xerrada",
    "videos.eyebrow": "Arxiu", "videos.title": "Vídeos i pòdcast", "videos.soon": "Pròximament",
    "videos.body": "Encara no hem enregistrat cap sessió. Aquí hi apareixeran els vídeos de les xerrades i els episodis del pòdcast a mesura que es publiquin.",
    "news.eyebrow": "Newsletter", "news.title": "No et perdis cap sessió", "news.body": "Un correu breu, un cop al mes, amb les properes xerrades i els vídeos publicats.",
    "news.name": "Nom", "news.email": "Correu electrònic", "news.cta": "Subscriu-te",
    "about.eyebrow": "Qui ho organitza", "about.title": "Una iniciativa de l'Associació Cave Cavet",
    "about.body": "L'Associació Cave Cavet impulsa i programa aquest cicle de xerrades, que té lloc a l'Hotel Termes Montbrió, que hi posa l'espai i les termes. Un cicle obert a hostes de l'hotel i a la comunitat local.",
    "collab.eyebrow": "Amb el suport de", "collab.title": "Col·laboracions",
    "collab.body": "Entitats, institucions i projectes que fan possible aquest cicle de xerrades.",
    "foot.orgs": "Una iniciativa de l'Associació Cave Cavet · amb la col·laboració de l'Hotel Termes Montbrió",
    "form.pending": "Formulari en preparació — s'enllaçarà properament.",
    "months": "GEN,FEB,MAR,ABR,MAI,JUN,JUL,AGO,SET,OCT,NOV,DES"
  },
  es: {
    "nav.tag": "Associació Cave Cavet", "nav.agenda": "Agenda", "nav.speaker": "Quiero ser speaker", "nav.videos": "Vídeos", "nav.contact": "Contacto",
    "hero.eyebrow": "Associació Cave Cavet, charlas\nEn el Hotel Termes Montbrió",
    "hero.title": "Charlas y talleres para pensar, cada mes",
    "hero.body": "Un espacio abierto de conversación, aprendizaje y comunidad en las termas de Montbrió. Sesiones gratuitas, con inscripción en línea.",
    "hero.cta1": "Ver la agenda", "hero.cta2": "Quiero ser speaker",
    "hero.next": "PRÓXIMA SESIÓN", "hero.nextCta": "Inscríbete",
    "hero.emptyTitle": "La próxima sesión se publicará pronto.",
    "agenda.eyebrow": "Programa", "agenda.title": "Próximas sesiones", "agenda.cta": "Inscripción",
    "agenda.empty": "Próximamente nuevas sesiones.",
    "tag.gratuito": "Gratuito",
    "speaker.eyebrow": "Abierto a la comunidad", "speaker.title": "¿Tienes algo que contar?",
    "speaker.body": "Buscamos voces cercanas — terapeutas, investigadores, artesanos, gente con un oficio o una idea que valga la pena compartir en 30 minutos.",
    "speaker.cta": "Propón tu charla",
    "videos.eyebrow": "Archivo", "videos.title": "Vídeos y podcast", "videos.soon": "Próximamente",
    "videos.body": "Todavía no hemos grabado ninguna sesión. Aquí aparecerán los vídeos de las charlas y los episodios del podcast a medida que se publiquen.",
    "news.eyebrow": "Newsletter", "news.title": "No te pierdas ninguna sesión", "news.body": "Un correo breve, una vez al mes, con las próximas charlas y los vídeos publicados.",
    "news.name": "Nombre", "news.email": "Correo electrónico", "news.cta": "Suscríbete",
    "about.eyebrow": "Quién lo organiza", "about.title": "Una iniciativa de la Associació Cave Cavet",
    "about.body": "La Associació Cave Cavet impulsa y programa este ciclo de charlas, que tiene lugar en el Hotel Termes Montbrió, que aporta el espacio y las termas. Un ciclo abierto a huéspedes del hotel y a la comunidad local.",
    "collab.eyebrow": "Con el apoyo de", "collab.title": "Colaboraciones",
    "collab.body": "Entidades, instituciones y proyectos que hacen posible este ciclo de charlas.",
    "foot.orgs": "Una iniciativa de la Associació Cave Cavet · con la colaboración del Hotel Termes Montbrió",
    "form.pending": "Formulario en preparación — se enlazará próximamente.",
    "months": "ENE,FEB,MAR,ABR,MAY,JUN,JUL,AGO,SEP,OCT,NOV,DIC"
  }
};

const STORAGE_KEY = "speakers-termes-lang";

function getLang() {
  return localStorage.getItem(STORAGE_KEY) || "ca";
}

function t(key) {
  return DICT[getLang()][key] || key;
}

function applyLang(lang) {
  document.documentElement.lang = lang;
  const dict = DICT[lang];
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (dict[key]) el.textContent = dict[key];
  });
  document.querySelectorAll("[data-i18n-ph]").forEach((el) => {
    const key = el.getAttribute("data-i18n-ph");
    if (dict[key]) el.setAttribute("placeholder", dict[key]);
  });
  document.querySelectorAll(".lang-toggle button").forEach((b) => {
    b.setAttribute("aria-pressed", String(b.getAttribute("data-lang") === lang));
  });
}

function setLang(lang) {
  localStorage.setItem(STORAGE_KEY, lang);
  applyLang(lang);
  window.dispatchEvent(new CustomEvent("langchange", { detail: { lang } }));
}

function initI18n() {
  applyLang(getLang());
  document.querySelectorAll(".lang-toggle button").forEach((b) => {
    b.addEventListener("click", () => setLang(b.getAttribute("data-lang")));
  });
}

window.I18N = { getLang, setLang, t, initI18n };
