# Plantilla de preguntes per als formularis

Per crear manualment a Nextcloud Forms o Google Forms (l'agent no té accés a cap
dels dos comptes). Un cop creat, enganxa l'URL resultant a `FORM_URLS` dins de
`js/app.js` (claus `speaker` / `newsletter` / `sesion_generica`).

## «Vull ser speaker» (clau `speaker`)

1. Nom i cognoms
2. Correu electrònic de contacte
3. Telèfon (opcional)
4. Tema o títol provisional de la xerrada/taller
5. Breu descripció (2-3 frases) del contingut
6. Durada aproximada
7. Necessitats tècniques (projector, música, espai per moure's, etc.)
8. Disponibilitat (mesos/dies de la setmana que et van bé)

## Inscripció a una sessió (clau `sesion_generica`)

1. Nom i cognoms
2. Correu electrònic
3. Sessió a la qual t'inscrius (desplegable o text lliure amb la data/títol)
4. Nombre d'acompanyants (si s'admeten)
5. Ets hoste de l'Hotel Termes Montbrió? (sí/no)
6. Acceptació de la política de privacitat

## Newsletter (clau `newsletter`)

1. Nom
2. Correu electrònic
3. Acceptació de la política de privacitat
