# Prevendita Lume — Stato del tracciamento e dei link

> Documento di passaggio di consegne per il reparto marketing.
> Dominio di produzione: **https://promo.lumefitness.it/**
> Ultimo aggiornamento: **2026-08-07** — verificato sul codice in produzione (branch `main`).

---

## 1. In sintesi

| Cosa | Stato |
|---|---|
| Google Tag Manager `GTM-K7P3RJNK` | ✅ installato su **tutte** le pagine |
| Meta Pixel `1498688582000036` | ⚠️ installato, ma invia **solo `PageView`** |
| Iubenda (privacy/cookie) | ✅ attivo su tutte le pagine |
| Google Analytics 4 | ❌ **nessun tag GA4 nel codice** — va creato dentro GTM |
| Eventi `dataLayer` per il funnel | ✅ già inviati dal sito (sezione 5) |
| UTM | ✅ letti, persistiti e propagati (sezione 4) |
| Meta: `InitiateCheckout` / `Purchase` / CAPI | ❌ da fare |
| UTM nei metadata Stripe | ❌ da fare |

**Il punto più importante:** il sito **manda già tutti gli eventi al `dataLayer`**, ma dentro GTM non risulta configurato nessun tag GA4. Finché non lo si crea, i dati del funnel non arrivano in Analytics. È il primo lavoro da fare (sezione 6).

---

## 2. Le pagine

Tutte servite da Netlify; gli URL funzionano **senza** `.html`.

| Pagina | URL | Ruolo nel funnel |
|---|---|---|
| Hub centri | `/` | Scelta del centro: card **Lume Urban** e **Lume Val di Chienti**. Propaga la query string (UTM inclusi) ai link |
| Prevendita Urban | `/urban` | Form prevendita **Lume Urban** — Macerata, centro storico |
| Prevendita Val di Chienti | `/val-di-chienti` | Form prevendita **Lume Val di Chienti** — Piediripa (ex "Motion") |
| Promo Lifestyle | `/promo?sede=macerata` | Landing promo **Lume Lifestyle** |
| Promo Element | `/promo?sede=montecassiano` | Landing promo **Lume Element** |
| Richiedi informazioni | `/richiedi-info?sede=urban` oppure `?sede=val-di-chienti` | Form **lead**, aperto dal pulsante nello step 2 dei form prevendita |
| Form PerfectGym | `/form` | Form generico interno/demo — **non usare in campagna** |

> ⚠️ `motion.html` **non esiste più**: la pagina è stata rinominata `val-di-chienti.html`. Qualsiasi link vecchio a `/motion` va aggiornato.

---

## 3. Offerta attuale — Fase 2

Prevendita in **Fase 2**, con scadenza **31 Agosto 2026**. Quota di attivazione **€50 → GRATIS** per chi si iscrive entro la scadenza.

### Lume Urban
| Piano | Prezzo | Equivalente mensile |
|---|---|---|
| 12 Mesi — Soluzione Unica | €390 | €32,50 / mese |
| 12 Mesi — 3 Rate | 3 × €140 = €420 | €35 / mese |

### Lume Val di Chienti
| Pacchetto | Piano | Prezzo | Equivalente mensile |
|---|---|---|---|
| Palestra + Corsi | Soluzione Unica | €480 | €40 / mese |
| Palestra + Corsi | 4 Rate | 4 × €130 = €520 | €43,33 / mese |
| Box Hybrid + Palestra | Soluzione Unica | €720 | €60 / mese |
| Box Hybrid + Palestra | 6 Rate | 6 × €130 = €780 | €65 / mese |

Nel messaggio pubblicitario la dicitura corretta è **"Prevendita"** (non più "Early Bird", cambiata in Fase 2).

---

## 4. Gestione UTM

### Come funziona
1. Ogni pagina del funnel, al caricamento, legge dall'URL i cinque parametri `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term`.
2. Li **unisce** a quelli già salvati e li **persiste** in `sessionStorage` (chiave `lume_utm`). L'URL corrente ha priorità sui valori vecchi.
3. Li rimanda al `dataLayer` con l'evento **`utm_context`** su *ogni* pagina, così si sa sempre da dove arriva l'utente anche quando l'URL non contiene più gli UTM.
4. Li allega a **tutti i webhook n8n**, quindi finiscono anche in Airtable insieme al lead.
5. La pagina hub `/` propaga la query string ai link dei due club: gli UTM sopravvivono al passaggio.

### Regola da rispettare nei link
Gli UTM vengono letti da `location.search`, cioè **devono stare prima del `#`**. Un link come `…/val-di-chienti#step-1-sede?utm_source=…` **non viene tracciato**.

✅ `…/val-di-chienti?utm_source=ig&utm_medium=social#step-1-sede`
❌ `…/val-di-chienti#step-1-sede?utm_source=ig&utm_medium=social`

L'hash `#step-1-sede` è comunque **superfluo**: la pagina non lo legge al caricamento, si apre allo step 1 in ogni caso. Meglio ometterlo, anche perché Meta aggiunge il proprio `fbclid` in coda e un fragment può interferire.

### Convenzione consigliata
| Parametro | Uso |
|---|---|
| `utm_source` | piattaforma: `facebook`, `instagram`, `whatsapp`, `google` |
| `utm_medium` | `paid_social` a pagamento · `social` organico · `referral` passaparola/segreteria |
| `utm_campaign` | campagna, es. `valdichienti_prevendita`, `urban_prevendita` |
| `utm_content` | creatività o posizionamento, es. `stories`, `reel_01`, `bio`, `segreteria` |
| `utm_term` | gruppo di inserzioni / pubblico |

---

## 5. Link pronti all'uso

### Inserzioni Meta (parametri dinamici)
Meta compila da solo campagna, adset e creatività. Incollare l'URL completo nel campo **URL del sito web** a livello di inserzione, **senza** usare anche il campo "Parametri URL" (altrimenti i parametri si duplicano).

**Val di Chienti**
```
https://promo.lumefitness.it/val-di-chienti?utm_source={{site_source_name}}&utm_medium=paid_social&utm_campaign={{campaign.name}}&utm_content={{ad.name}}&utm_term={{adset.name}}
```

**Urban**
```
https://promo.lumefitness.it/urban?utm_source={{site_source_name}}&utm_medium=paid_social&utm_campaign={{campaign.name}}&utm_content={{ad.name}}&utm_term={{adset.name}}
```

`{{site_source_name}}` diventa `fb` o `ig` a seconda di dove viene mostrata l'inserzione.

### Organico (Storie, bio, WhatsApp)
I parametri dinamici non esistono fuori dalle inserzioni: vanno scritti a mano.

```
https://promo.lumefitness.it/val-di-chienti?utm_source=instagram&utm_medium=social&utm_campaign=valdichienti_prevendita&utm_content=stories
```
```
https://promo.lumefitness.it/urban?utm_source=instagram&utm_medium=social&utm_campaign=urban_prevendita&utm_content=bio
```
```
https://promo.lumefitness.it/val-di-chienti?utm_source=whatsapp&utm_medium=referral&utm_campaign=valdichienti_prevendita&utm_content=segreteria
```

---

## 6. Eventi inviati al `dataLayer`

Il sito **non ha GA4 installato**: spinge gli eventi nel `dataLayer` e sta a GTM raccoglierli e inoltrarli.

| Evento | Dove | Quando | Campi |
|---|---|---|---|
| `select_club` | `/` | click su una card centro | `club` |
| `utm_context` | tutte le pagine funnel | caricamento pagina | `page`, `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term` |
| `form_step` | tutti i form | a ogni step | `form_id`, `form_sede`, `step_number`, `step_name`, `step_slug`, `virtual_page` |
| `form_thank_you` | tutti i form | completamento (hash `#grazie`) | come sopra → **conversione** |
| `form_lead` | `/richiedi-info` | invio richiesta info | `form_sede`, `sede_key`, `piano_key`, `abbonamento_interesse` + tutti gli UTM → **lead** |
| `form_exit` | `/urban`, `/val-di-chienti` | uscita dalla pagina | `furthest_step`, `furthest_slug`, `completed` + UTM → **abbandoni** |

### Cosa configurare in GTM
1. **Variabile GA4 Configuration** con il measurement ID della property (non è nel codice: recuperarlo da GA4 → Amministrazione → Origini dati).
2. **Trigger Custom Event** per ciascun evento della tabella.
3. **Tag GA4 Event** per ognuno, mappando i campi come parametri evento.
4. Registrare i parametri come **Dimensioni personalizzate** in GA4 (`form_id`, `form_sede`, `step_slug`, `furthest_slug`, `piano_key`), altrimenti non compaiono nei report. Non sono retroattive.
5. Segnare **`form_thank_you`** e **`form_lead`** come *Key event* (conversioni).
6. Costruire una **Funnel exploration** con `form_step` filtrando su `step_slug` (sezione 7).

---

## 7. Step dei form → hash URL

Ogni cambio step aggiorna l'hash senza ricaricare la pagina: è la base per il funnel e per capire dove si fermano le persone.

### `/urban` e `/val-di-chienti`
| Step | Schermata | Hash |
|---|---|---|
| 1 | Sede | `#step-1-sede` |
| 2 | Abbonamento | `#step-2-abbonamento` |
| 3 | Dati personali | `#step-3-dati` |
| 4 | Contratto + firma | `#step-4-contratto` |
| 5 | **Thank you / Iscritto** | `#grazie` |
| 6 | Non disponibile (già iscritto) | `#non-disponibile` |
| 7 | Pagamento non confermato | `#pagamento-non-confermato` |

### `/promo`
`#step-1-promo` → `#step-2-form` → `#grazie`

### `/richiedi-info`
`#richiedi-info` → `#grazie`

### `/form` (interno)
`#step-1-sede` → `#step-2-abbonamento` → `#step-3-dati` → `#step-4-riepilogo` → `#step-5-pagamento` → `#grazie`

> **La thank you page è sempre l'hash `#grazie`**, su tutti i form.

### Analisi del drop-off
- **Funnel exploration** su `form_step` con gli `step_slug` in sequenza: mostra quanti proseguono e dove calano.
- **`form_exit`** dà il punto più avanzato raggiunto anche da chi non completa: raggruppando per `furthest_slug` si vede lo step che perde più persone.

---

## 8. Dove finiscono i dati

### Webhook n8n (`https://n8n.lumeflow.it`)
| Momento | Webhook |
|---|---|
| Step 3 — verifica se già iscritto | `/webhook/verifica-iscritto` |
| Step 3 — anagrafica | `/webhook/iscrizione` |
| Step 4 — contratto firmato | `/webhook/FIRMA-CONTRATTO` |
| Pagamento (in sede o ritorno Stripe) | `/webhook/conferma-stripe` |
| Submit promo | `/webhook/promo-prova` |
| Submit richiedi info | `/webhook/richiestainfo` |

Tutti i payload includono gli UTM persistiti.

### Airtable — base **LUME FITNESS**, tabella **Prevendita Urban**
Raccoglie i lead e le iscrizioni. Campi utili al marketing: `UTM Source/Medium/Campaign/Content/Term`, `Sede`, `Piano`, `Importo`, `Abbonamento Interesse`, `Stato`, `Data Iscrizione`.

Valori del campo **Stato**: `Pagamento completato` · `In attesa` · `Contratto firmato` · `Annullato` · `Non Interessato` · `Bloccato`.

Guardie anti-invio-doppio gestite da n8n: `Invia email conferma`, `Conferma inviata`, `Email Info Lead Inviata`. Il campo **`Email Disiscritto`** segna chi ha fatto unsubscribe: **va escluso da ogni invio** (`NOT({Email Disiscritto})` nei filtri).

---

## 9. Flusso di pagamento (Stripe)

1. Allo step 4 il form chiama `POST /api/create-checkout` → crea la Stripe Checkout Session.
2. L'utente viene portato sulla pagina di pagamento Stripe.
3. Al ritorno:
   - **successo** → `?payment=success&session_id=…` → thank you (`#grazie`) e webhook `conferma-stripe`;
   - **annullato** → `?payment=cancel` → schermata "Pagamento non confermato" (`#pagamento-non-confermato`). I dati sono già stati salvati negli step precedenti, quindi la persona è comunque ricontattabile.

È previsto anche il **pagamento in sede** (contanti/POS/bonifico), che salta Stripe e va diretto al thank you.

---

## 10. Cosa manca — lista di lavoro

| Priorità | Attività | Perché |
|---|---|---|
| **Alta** | Creare i tag GA4 in GTM (sezione 6) | Oggi gli eventi partono ma **non arrivano in Analytics**: nessun dato di funnel |
| **Alta** | Registrare le dimensioni personalizzate in GA4 | Senza, i parametri non sono usabili nei report — e non sono retroattive |
| Media | Eventi Meta `InitiateCheckout` e `Purchase` | Oggi il Pixel manda solo `PageView`: campagne non ottimizzabili sulla conversione |
| Media | Meta CAPI server-side (via n8n) | Attribuzione indipendente dal browser |
| Media | UTM + `fbp`/`fbc` nei metadata Stripe | Oggi sopravvivono solo in `sessionStorage`, si perdono nel round-trip |
| Bassa | Verificare il campo `Fase Prevendita` in Airtable | Risulta **vuoto su tutti i record**: la costante `RELEASE` è inviata solo da `/urban`, non da `/val-di-chienti` |
| Bassa | Aggiornare eventuali link a `/motion` | La pagina è stata rinominata `/val-di-chienti` |

---

## 11. Note operative

- **Fail-open sulla verifica iscritto**: se n8n non risponde, l'utente prosegue comunque. Meglio un'iscrizione doppia che una persona bloccata.
- **Le persone cambiano email tra un tentativo e l'altro.** Nei controlli sui duplicati non affidarsi all'email: usare **codice fiscale** o **telefono**. In tabella sono già emersi casi di stessa persona con due indirizzi diversi.
- **`/form` è interno**: non va usato in campagna.
- Il Pixel Meta e GTM sono inseriti direttamente nell'HTML di ogni pagina, non tramite variabili d'ambiente: cambiarli richiede una modifica al codice.
