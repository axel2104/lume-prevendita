# Tracking & Funnel GA4 — Lume Prevendita

> Documento per il reparto marketing.
> Dominio di produzione: **https://promo.lumefitness.it/**
> Ultimo aggiornamento: 2026-07-17

---

## 0. Nota importante — GTM non è più in uso

Le versioni precedenti di questo documento indicavano **Google Tag Manager (`GTM-K7P3RJNK`)** come sistema di tracking. Questo **non è più vero**: il codice è stato aggiornato e oggi il sito usa **Google tag (gtag.js) diretto**, senza passare da un container GTM.

In pratica:
- Non c'è nessun container GTM da aprire o modificare.
- Gli eventi vengono inviati **direttamente a GA4** tramite `gtag('event', ...)`, oltre che al `dataLayer` (mantenuto per compatibilità/debug).
- Tutta la configurazione del funnel va quindi fatta **dentro GA4** (Admin + Esplorazioni), non in GTM.

Se in futuro il team volesse reintrodurre GTM come layer di gestione tag (ad es. per aggiungere rapidamente nuovi pixel senza toccare il codice), è possibile, ma è un intervento di sviluppo separato — non necessario per costruire il funnel oggi.

---

## 1. Tag installati (tutte le pagine)

| Strumento | ID | Stato |
|---|---|---|
| Google tag (gtag.js → GA4) | `G-V7GT05VPZ2` | ✅ attivo su tutte le pagine, invia `page_view` automatico + eventi custom |
| Meta Pixel | `1498688582000036` | ✅ attivo — invia `PageView` al caricamento di ogni pagina |

> ⚠️ Eventi Meta avanzati (`InitiateCheckout`, `Purchase`) e **CAPI server-side**: **non ancora attivi**, in attesa del piano marketing. Oggi il sito manda a GA4 solo gli eventi descritti nella sezione 4; a Meta arriva solo `PageView`.

---

## 2. Mappa delle pagine e dei link

| Pagina | URL | Funzione |
|---|---|---|
| Home | `https://promo.lumefitness.it/` | Redirect automatico verso `urban.html` (preserva UTM) |
| Prevendita Urban | `https://promo.lumefitness.it/urban.html` | Form prevendita **Lume Urban** (Macerata) |
| Prevendita Motion | `https://promo.lumefitness.it/motion.html` | Form prevendita **Lume Motion** (Piediripa) — pagina esistente, attualmente non linkata dalla home |
| Promo Lifestyle | `https://promo.lumefitness.it/promo.html?sede=macerata` | Pagina promo **Lume Lifestyle** (sede attiva) |
| Promo Element | `https://promo.lumefitness.it/promo.html?sede=montecassiano` | Pagina promo **Lume Element** (sede attiva) |
| Form PerfectGym | `https://promo.lumefitness.it/form.html` | Form generico PerfectGym (demo/interno) |
| Richiedi informazioni | `https://promo.lumefitness.it/richiedi-info.html?sede=urban` | Form **lead** (nome, cognome, email, telefono) — aperto dal pulsante "Richiedi informazioni" nello step 2 |

### Propagazione UTM
- Ogni pagina del funnel (`urban`, `motion`, `promo`, `richiedi-info`) al caricamento: legge gli UTM dall'URL, li **fonde e persiste** in `sessionStorage` (`lume_utm`) e invia un evento **`utm_context`** (dataLayer + GA4) con `{ page, utm_source, utm_medium, utm_campaign, utm_term, utm_content }` → così GA4 sa **da dove arriva l'utente su ogni pagina**, anche quando l'URL corrente non contiene più gli UTM.
- Gli UTM persistiti vengono **inclusi in tutti i webhook n8n** (verifica-iscritto, iscrizione, FIRMA-CONTRATTO, conferma-stripe, promo-prova, lead).
- La home (`index.html`) reindirizza a `urban.html` preservando la query (UTM inclusi).
- ⚠️ **Ancora da fare**: inserire gli UTM nei **metadata della sessione Stripe** (vedi sezione 6) — oggi sul round-trip di pagamento sopravvivono solo via `sessionStorage`.

---

## 3. Step di ogni form → URL (hash)

Ogni passaggio di step aggiorna l'**hash dell'URL** (senza ricaricare la pagina), ed è accompagnato da un evento GA4.

### `urban.html` e `motion.html`
| Step | Schermata | URL hash |
|---|---|---|
| 1 | Sede | `#step-1-sede` |
| 2 | Abbonamento | `#step-2-abbonamento` |
| 3 | Dati personali | `#step-3-dati` |
| 4 | Contratto + firma | `#step-4-contratto` |
| 5 | **Thank you / Iscritto** | `#grazie` |
| 6 | Non disponibile (già iscritto) | `#non-disponibile` |
| 7 | **Pagamento non confermato** (annulla/chiude Stripe) | `#pagamento-non-confermato` |

### `form.html`
| Step | Schermata | URL hash |
|---|---|---|
| 1 | Sede | `#step-1-sede` |
| 2 | Abbonamento | `#step-2-abbonamento` |
| 3 | Dati | `#step-3-dati` |
| 4 | Riepilogo | `#step-4-riepilogo` |
| 5 | Pagamento | `#step-5-pagamento` |
| 6 | **Thank you** | `#grazie` |

### `promo.html`
| Step | Schermata | URL hash |
|---|---|---|
| 1 | Info promo | `#step-1-promo` |
| 2 | Form contatto | `#step-2-form` |
| 3 | **Thank you / Richiesta inviata** | `#grazie` |

### `richiedi-info.html` (lead)
| Step | Schermata | URL hash |
|---|---|---|
| 1 | Form richiesta info | `#richiedi-info` |
| 2 | **Richiesta inviata (lead)** | `#grazie` |

> **Thank you page = URL con hash `#grazie`** in tutti i form → è la pagina/evento di conversione da usare in GA4.

---

## 4. Eventi inviati a GA4

A ogni cambio step il sito chiama `gtag('event', ...)` (oltre a un push equivalente su `dataLayer`, mantenuto per debug):

```js
// Ad ogni step:
gtag('event', 'form_step', {
  form_id: 'urban',            // urban | motion | form | promo | richiedi-info
  form_sede: 'Lume Urban',     // nome sede
  step_number: 3,              // numero step
  step_slug: 'step-3-dati'     // = hash URL
});

// Al completamento (thank you):
gtag('event', 'form_thank_you', { form_id: 'urban', form_sede: 'Lume Urban', step_number: 5, step_slug: 'grazie' });
```

| Evento GA4 | Quando scatta | Parametri principali | Uso consigliato |
|---|---|---|---|
| `page_view` | automatico, ad ogni pagina caricata | standard GA4 | traffico su ogni pagina del funnel |
| `form_step` | a ogni step di ogni form | `form_id`, `form_sede`, `step_number`, `step_slug`, `virtual_page` | passo del **funnel di esplorazione** |
| `form_thank_you` | sul completamento (step finale, hash `#grazie`) | `form_id`, `form_sede`, `step_slug` | **evento di conversione** (da segnare come Key Event) |
| `generate_lead` | invio del form "Richiedi informazioni" | `form_id`, `form_sede`, `piano_key`, `piano_nome`, `utm_source/medium/campaign/content/term` | **evento Lead** — attribuzione completa + piano richiesto (già mappato sul nome evento standard GA4 `generate_lead`, quindi riconosciuto automaticamente dai report Acquisizione) |
| `utm_context` | caricamento di **ogni** pagina | `page`, `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content` | sapere da dove arriva l'utente su ogni pagina, anche senza UTM nell'URL corrente |
| `form_exit` | quando l'utente lascia/chiude la pagina del form (urban/motion) | `form_id`, `form_sede`, `furthest_step`, `furthest_slug`, `completed` | **drop-off/abbandoni**: punto più avanzato raggiunto da chi non completa |

### Valori di `form_id` / `form_sede`
| Pagina | `form_id` | `form_sede` |
|---|---|---|
| `urban.html` | `urban` | `Lume Urban` |
| `motion.html` | `motion` | `Lume Motion` |
| `form.html` | `form` | nome club selezionato (dinamico) |
| `promo.html` | `promo` | `Lume Lifestyle` / `Lume Element` (da `?sede=`) |
| `richiedi-info.html` | `richiedi-info` | nome sede (da `?sede=`) |

---

## 5. Come costruire il funnel su GA4 — passo passo

Presupposto: nella property GA4 collegata a `G-V7GT05VPZ2` gli eventi sopra arrivano **già automaticamente**, senza bisogno di GTM. Vanno solo **configurati i report**.

### 5.1 Verificare che i dati arrivino
1. GA4 → **Amministrazione → Origini dati (Data streams)** → controlla che lo stream web abbia measurement ID `G-V7GT05VPZ2`.
2. GA4 → **Rapporti → In tempo reale**: apri il sito, avanza in un form e verifica che compaiano `page_view`, `form_step`, `form_thank_you`.

### 5.2 Registrare le dimensioni personalizzate
GA4 riceve i parametri evento (es. `form_id`, `step_slug`, `furthest_slug`, `piano_key`) ma per poterli usare nei report/esplorazioni vanno **registrati come Dimensioni personalizzate**:

GA4 → **Amministrazione → Definizioni personalizzate → Dimensioni personalizzate → Crea**. Crea una dimensione per ciascuno di questi parametri evento (ambito = "Evento"):

| Nome dimensione (suggerito) | Parametro evento |
|---|---|
| Form ID | `form_id` |
| Sede form | `form_sede` |
| Step numero | `step_number` |
| Step slug | `step_slug` |
| Furthest step | `furthest_step` |
| Furthest slug | `furthest_slug` |
| Completato | `completed` |
| Piano scelto | `piano_key` / `piano_nome` |
| UTM Source / Medium / Campaign | `utm_source` / `utm_medium` / `utm_campaign` |

> Nota: GA4 mostra dati nelle dimensioni personalizzate solo **da quando vengono create in poi** (non è retroattivo).

### 5.3 Segnare gli eventi di conversione (Key Event)
GA4 → **Amministrazione → Eventi (Events)** → trova `form_thank_you` e `generate_lead` → attiva l'interruttore **"Segna come Key event"** (in GA4 vecchia UI: "Contrassegna come conversione"). Da qui in poi compaiono nei report standard di conversione e possono essere usati come obiettivi in Google Ads.

### 5.4 Creare l'esplorazione Funnel (dove si fermano le persone)
GA4 → **Esplora → Nuova esplorazione → Funnel exploration**.

Per il funnel `urban` (stesso procedimento per `motion`/`form`/`promo`), imposta come step condition **`form_step` con parametro `step_slug` uguale a**:

1. `step-1-sede`
2. `step-2-abbonamento`
3. `step-3-dati`
4. `step-4-contratto`
5. `grazie` *(o direttamente l'evento `form_thank_you`)*

Aggiungi un filtro globale `form_id` esatto = `urban` per non mischiare i dati con `motion`/`form`. Il grafico a imbuto mostrerà quante sessioni proseguono a ogni step e la % di abbandono step-per-step.

### 5.5 Analizzare gli abbandoni con `form_exit`
GA4 → **Esplora → Nuova esplorazione → Free form (tabella libera)**:
- Righe: dimensione **Furthest slug**
- Metrica: Conteggio eventi (filtrato su evento = `form_exit`)
- Filtro secondario: `form_id` = `urban` (o altro form)

Questo mostra, per chi **non** ha completato il form, esattamente su quale step si è fermato di più — utile per capire dove intervenire (es. troppi abbandoni allo step firma contratto).

### 5.6 Report lead e attribuzione
Per vedere i lead per sorgente/piano richiesto: **Esplora → Free form**, evento = `generate_lead`, righe = dimensioni `piano_key` + `Sessione origine/mezzo` (o le dimensioni UTM custom sopra).

---

## 6. Tracciamento server-side esistente (n8n)

Oltre agli eventi GA4, i form inviano già dati lato server a **n8n** (`https://n8n.lumeflow.it`). Utile per il CRM/Airtable e come base per la futura CAPI Meta.

| Momento | Webhook n8n | Note |
|---|---|---|
| Step 3 — verifica | `/webhook/verifica-iscritto` | controlla se già iscritto (urban/motion) |
| Step 3 — anagrafica | `/webhook/iscrizione` | registra i dati inseriti |
| Step 4 — firma | `/webhook/FIRMA-CONTRATTO` | invio contratto firmato |
| Pagamento (in sede / ritorno Stripe) | `/webhook/conferma-stripe` | conferma iscrizione + `session_id` |
| Submit promo | `/webhook/promo-prova` | lead dalla pagina promo |
| Submit "Richiedi informazioni" | `/webhook/richiestainfo` | lead — **già configurato e attivo** |

---

## 7. Flusso di pagamento (Stripe)

1. Allo step 4, il form chiama `POST /api/create-checkout` (Netlify Function) → crea la **Stripe Checkout Session**.
2. L'utente viene reindirizzato alla pagina di pagamento Stripe.
3. Al ritorno:
   - **Successo** → `https://promo.lumefitness.it/{sede}.html?payment=success&session_id=...` → la pagina mostra il thank you (`#grazie`) e chiama `conferma-stripe`.
   - **Annullato / chiusura Stripe** → `https://promo.lumefitness.it/{sede}.html?payment=cancel` → l'utente **non torna al form** ma finisce sulla pagina **"Pagamento non confermato"** (`#pagamento-non-confermato`) con messaggio *"ti ricontatteremo telefonicamente"*. I dati sono già stati salvati negli step precedenti (webhook `iscrizione` + `FIRMA-CONTRATTO`).

> ⚠️ **Da allineare con marketing:** gli UTM e gli identificatori Meta (`fbp`/`fbc`) **non viaggiano ancora** nei metadata della sessione Stripe. Inserirli renderebbe l'attribuzione e la futura CAPI indipendenti dal browser.

---

## 8. Riepilogo — cosa fare in GA4 (checklist)

1. ☐ Verificare in **Rapporti in tempo reale** che gli eventi arrivino correttamente.
2. ☐ Creare le **dimensioni personalizzate** elencate al punto 5.2.
3. ☐ Segnare **`form_thank_you`** e **`generate_lead`** come **Key event**.
4. ☐ Creare l'**esplorazione Funnel** per ciascun form (`urban`, `motion`, `promo`, `form`) usando `step_slug`.
5. ☐ Creare l'**esplorazione drop-off** con `form_exit` / `furthest_slug`.
6. ☐ (Da pianificare, richiede sviluppo) eventi Meta `InitiateCheckout` / `Purchase` + CAPI server-side via n8n; UTM e `fbp`/`fbc` nei metadata Stripe.
