# Lume — Form di Prevendita (PerfectGym v2.2)

Form multistep brandizzato per la prevendita Lume + backend che crea **membro + contratto** in
PerfectGym e avvia il **pagamento dell'acconto**.

> **Stato attuale: DEMO.** `index.html` ha `CONFIG.DEMO_MODE = true`: funziona da solo su GitHub
> Pages, **senza backend**, senza addebiti e senza scrivere nulla in PerfectGym. Serve a mostrare
> il flusso. Per attivarlo davvero: imposta `DEMO_MODE = false`, fai il deploy del backend (sezione
> sotto) e collega `API_BASE`.

```
repo/
  index.html             ← il form (statico)        → GitHub Pages
  api/register.js         ← crea membro+contratto    → Vercel (serverless)
  api/payment-plans.js    ← helper config
  lib/perfectgym.js       ← client API PerfectGym
  lib/mapper.js           ← validazione + mapping
  test/test-mapper.js     ← test offline (npm test)
  package.json  vercel.json  .env.example  .gitignore
```

## ⚠️ Perché servono DUE deploy

GitHub Pages serve **solo file statici**: ospita benissimo `index.html`, ma **non esegue** il
backend Node. Inoltre il backend custodisce le credenziali PerfectGym (`X-Client-Id/Secret`), che
**non devono mai** finire nel browser. Quindi:

- **Frontend (`index.html`) → GitHub Pages**
- **Backend (`api/`) → Vercel** (gratis, si collega allo *stesso* repo GitHub)

Il form su Pages chiama il backend su Vercel (campo `CONFIG.API_BASE`).

---

## 1) Carica su GitHub

Crea su github.com un repo vuoto `lume-prevendita`, poi dalla cartella del progetto:

```bash
git init
git add .
git commit -m "Lume prevendita: form + backend PerfectGym"
git branch -M main
git remote add origin https://github.com/<tuo-utente>/lume-prevendita.git
git push -u origin main
```

## 2) Attiva GitHub Pages (frontend)

Repo → **Settings → Pages** → *Build and deployment* → **Deploy from a branch** →
branch **main**, cartella **/(root)** → Save.
Dopo ~1 minuto il form è online su `https://<tuo-utente>.github.io/lume-prevendita/`.

## 3) Deploy del backend su Vercel

1. vercel.com → **Add New → Project → Import** il repo `lume-prevendita`.
2. **Environment Variables** (vedi `.env.example`):
   - `PG_CLIENT_ID`, `PG_CLIENT_SECRET` — le stesse della dashboard (`C:\Users\Alex\Desktop\CLAUDE\.env`)
   - `PG_API_BASE` = `https://lumefitness.perfectgym.com/Api`
   - `ALLOWED_ORIGIN` = `https://<tuo-utente>.github.io` (il dominio del form su Pages)
   - `THANK_YOU_URL` = pagina di ritorno dopo il pagamento
3. Deploy → ottieni un URL tipo `https://lume-prevendita.vercel.app`.

> Vercel ridistribuisce in automatico ad ogni `git push`: il backend resta "su GitHub".

## 4) Collega il form al backend

In `index.html` → `CONFIG.API_BASE` metti l'URL Vercel, poi `git push`:

```js
API_BASE: 'https://lume-prevendita.vercel.app',
```

## 5) Inserisci i Payment Plan ID

Chiama una volta:

```
https://lume-prevendita.vercel.app/api/payment-plans?clubId=2
```

Copia gli `id` dei 4 piani di prevendita in `index.html` → `CONFIG.CLUBS[].plans[].pgPaymentPlanId`,
poi `git push`.

---

## Test prima del pubblico

- **Offline (logica):** `npm test` → 8 test, nessuna rete.
- **Reale:** una prevendita di prova su `clubId=2` con CF di test → verifica membro+contratto in
  PerfectGym → poi apri al pubblico.

## Note / limiti

- **Acconto**: gli endpoint non addebitano un importo arbitrario al volo; l'acconto/prima rata è quello
  del **Payment Plan PerfectGym** del contratto. Per una caparra fissa, crea un Payment Plan di
  prevendita con prima rata = acconto e usane l'`id`.
- **Quota attivazione €50**: da gestire post-prevendita (addon/voucher o step staff).
- **Sedi**: finché Macerata/Piediripa non sono club PerfectGym, tutto va su `clubId=2`.
- **PCI-safe**: i dati carta si inseriscono sulla pagina hosted di PerfectGym, mai sui nostri server.
  In alternativa è pronto l'incasso via IBAN/SEPA (`addDirectDebit` in `lib/perfectgym.js`).

## Alternativa: tutto su Vercel (senza Pages)

Se preferisci un solo deploy, Vercel serve sia `index.html` sia `api/`: importa il repo e basta,
con `API_BASE: ''`. In quel caso GitHub Pages non serve.

---

## Link riservato alle consulenti (iscrizioni in sede dopo la scadenza)

La prevendita pubblica si chiude da sola alla `data-deadline` della pagina (Urban: 14/09/2026).
Le consulenti continuano a iscrivere in struttura con un link che porta un token segreto:

```
https://promo.lumefitness.it/urban?canale=sede&k=TOKEN&utm_source=sede&utm_medium=consulente&utm_campaign=urban_prevendita
```

Con `canale=sede` **e** `k` valorizzato la pagina:

- nasconde il countdown e non si auto-chiude;
- tiene attivo il pulsante "Acquista la prevendita";
- mostra i metodi di pagamento in sede (contanti, POS, bonifico) sui piani in soluzione unica;
- mostra la fascia "Modalità sede" in alto, così si vede subito di essere sul link giusto;
- manda `canale: "sede"` a n8n anche sul ramo Stripe.

Senza `k` la pagina resta chiusa esattamente come per il pubblico.

### Impostare il token

1. Genera un valore casuale:
   ```bash
   node -e "console.log(require('crypto').randomBytes(12).toString('base64url'))"
   ```
2. Mettilo come variabile d'ambiente **`SEDE_TOKEN`** sul deploy del backend, poi ridistribuisci.
3. Usa lo stesso valore nel `?k=` del link salvato su Airtable.

Il token serve solo al pagamento con carta: `/api/create-checkout` risponde `410` dopo la
scadenza a meno che `sede_token` non coincida con `SEDE_TOKEN` (confronto a tempo costante).
Contanti, POS e bonifico non passano dal backend, quindi funzionano anche senza token —
ma senza `k` nel link la pagina non li mostra nemmeno.

Se `SEDE_TOKEN` non è impostato nessun token passa e vale solo la scadenza pubblica:
il pagamento con carta dà errore, gli altri tre metodi restano utilizzabili.

### Dove mettere il link in Airtable

Base **LUME FITNESS** → tabella **Prevendita Urban**. Il link è uguale per tutte le consulenti:
tienilo nella descrizione della vista o in un campo URL fisso, non in un campo per record.
Chiunque abbia il link può acquistare: trattalo come una password, e per revocarlo cambia
`SEDE_TOKEN` e aggiorna il link.
