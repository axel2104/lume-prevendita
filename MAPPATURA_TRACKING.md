# Mappatura Tracking & Link — Lume Prevendita

> Documento per il reparto marketing / configurazione GTM.
> Dominio di produzione: **https://promo.lumefitness.it/**
> Ultimo aggiornamento: 2026-06-30

---

## 1. Tag installati (tutte le pagine)

| Strumento | ID | Stato |
|---|---|---|
| Google Tag Manager | `GTM-K7P3RJNK` | ✅ attivo su tutte le pagine (`<head>` + `<noscript>`) |
| Meta Pixel | `1498688582000036` | ✅ attivo — invia `PageView` al caricamento di ogni pagina |

> ⚠️ Eventi Meta avanzati (`InitiateCheckout`, `Purchase`) e **CAPI server-side**: **non ancora attivi**, in attesa del piano marketing. Oggi la landing manda a GTM solo gli eventi `dataLayer` descritti sotto (sezione 4).

---

## 2. Mappa delle pagine e dei link

| Pagina | URL | Funzione |
|---|---|---|
| Home | `https://promo.lumefitness.it/` | Mostra la card **Lume Urban** → CTA verso `urban.html` |
| Prevendita Urban | `https://promo.lumefitness.it/urban.html` | Form prevendita **Lume Urban** (Macerata) |
| Prevendita Motion | `https://promo.lumefitness.it/motion.html` | Form prevendita **Lume Motion** (Piediripa) — pagina esistente, attualmente non linkata dalla home |
| Promo Lifestyle | `https://promo.lumefitness.it/promo.html?sede=macerata` | Pagina promo **Lume Lifestyle** (sede attiva) |
| Promo Element | `https://promo.lumefitness.it/promo.html?sede=montecassiano` | Pagina promo **Lume Element** (sede attiva) |
| Form PerfectGym | `https://promo.lumefitness.it/form.html` | Form generico PerfectGym (demo/interno) |

### Propagazione UTM
- La home (`index.html`) **propaga automaticamente** i parametri `utm_source, utm_medium, utm_campaign, utm_term, utm_content, canale` sul link CTA verso `urban.html`.
- I form (`urban.html`, `motion.html`) salvano gli UTM in `sessionStorage` e li inoltrano ai webhook n8n. *(Nota: non ancora inseriti nei metadata Stripe — vedi sezione 6.)*

---

## 3. Step di ogni form → URL (hash)

Ogni passaggio di step aggiorna l'**hash dell'URL** (senza ricaricare la pagina). Questo permette a GTM (trigger **History Change**) di tracciare il funnel e capire **dove si ferma l'utente**.

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

> **Thank you page = URL con hash `#grazie`** in tutti i form → da usare come pagina di conversione in GTM/GA4.

---

## 4. Eventi `dataLayer` (per GTM)

A ogni cambio step viene fatto un push su `dataLayer`:

```js
// Ad ogni step:
{
  event: 'form_step',
  form_id: 'urban',            // urban | motion | form | promo
  form_sede: 'Lume Urban',     // nome sede
  step_number: 3,              // numero step
  step_name: 'Dati Personali', // nome leggibile
  step_slug: 'step-3-dati',    // = hash URL
  virtual_page: '/urban.html#step-3-dati'
}

// In più, al completamento (thank you):
{ event: 'form_thank_you', form_id: 'urban', form_sede: 'Lume Urban', step_number: 5, step_slug: 'grazie', ... }
```

| Evento | Quando scatta | Uso consigliato in GTM |
|---|---|---|
| `form_step` | a ogni step di ogni form | page_view virtuale / evento funnel GA4 |
| `form_thank_you` | sul completamento (step finale) | **evento di conversione** |

### Valori di `form_id` / `form_sede`
| Pagina | `form_id` | `form_sede` |
|---|---|---|
| `urban.html` | `urban` | `Lume Urban` |
| `motion.html` | `motion` | `Lume Motion` |
| `form.html` | `form` | nome club selezionato (dinamico) |
| `promo.html` | `promo` | `Lume Lifestyle` / `Lume Element` (da `?sede=`) |

---

## 5. Tracciamento server-side esistente (n8n)

Oltre agli eventi GTM, i form inviano già dati lato server a **n8n** (`https://n8n.lumeflow.it`). Utile per il CRM/Airtable e come base per la futura CAPI Meta.

| Momento | Webhook n8n | Note |
|---|---|---|
| Step 3 — verifica | `/webhook/verifica-iscritto` | controlla se già iscritto (urban/motion) |
| Step 3 — anagrafica | `/webhook/iscrizione` | registra i dati inseriti |
| Step 4 — firma | `/webhook/FIRMA-CONTRATTO` | invio contratto firmato |
| Pagamento (in sede / ritorno Stripe) | `/webhook/conferma-stripe` | conferma iscrizione + `session_id` |
| Submit promo | `/webhook/promo-prova` | lead dalla pagina promo |

---

## 6. Flusso di pagamento (Stripe)

1. Allo step 4, il form chiama `POST /api/create-checkout` (Netlify Function) → crea la **Stripe Checkout Session**.
2. L'utente viene reindirizzato alla pagina di pagamento Stripe.
3. Al ritorno:
   - **Successo** → `https://promo.lumefitness.it/{sede}.html?payment=success&session_id=...` → la pagina mostra il thank you (`#grazie`) e chiama `conferma-stripe`.
   - **Annullato / chiusura Stripe** → `https://promo.lumefitness.it/{sede}.html?payment=cancel` → l'utente **non torna al form** ma finisce sulla pagina **"Pagamento non confermato"** (`#pagamento-non-confermato`) con messaggio *"ti ricontatteremo telefonicamente"*. I dati sono già stati salvati negli step precedenti (webhook `iscrizione` + `FIRMA-CONTRATTO`).

> ⚠️ **Da allineare con marketing/Alexia:** gli UTM e gli identificatori Meta (`fbp`/`fbc`) **non viaggiano ancora** nei metadata della sessione Stripe. Inserirli renderebbe l'attribuzione e la futura CAPI indipendenti dal browser. (Vedi punto in sezione 1.)

---

## 7. Riepilogo per GTM — cosa configurare

1. **Trigger History Change** → mappare `form_step` su un evento GA4 (es. `view_form_step`) con i parametri `form_id`, `form_sede`, `step_number`, `step_slug` → abilita analisi funnel/drop-off.
2. **Trigger Custom Event = `form_thank_you`** → evento di **conversione** GA4 / Meta.
3. Pagine di conversione identificabili dall'hash **`#grazie`**.
4. (Da pianificare) eventi Meta `InitiateCheckout` / `Purchase` + CAPI server-side via n8n.
