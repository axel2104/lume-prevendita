'use strict';
/**
 * POST /api/create-checkout
 * Crea una Stripe Checkout Session e restituisce l'URL di pagamento.
 * - rate === 1  → mode: 'payment',      importo unico
 * - rate > 1   → mode: 'subscription', €130/mese × N rate
 *
 * Body params:
 *   email, nome, cognome, piano_id, sede, page
 *   (importo e rate NON si leggono dal client: derivano da PIANI[piano_id])
 *
 * Env vars richieste:
 *   STRIPE_SECRET_KEY   — secret key Stripe (sk_live_... / sk_test_...)
 *   ALLOWED_ORIGIN      — opzionale, default '*'
 */
const CORS = {
  'Access-Control-Allow-Origin': process.env.ALLOWED_ORIGIN || '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Content-Type': 'application/json',
};

/* Scadenza prevendita per sede: dopo questa data niente checkout online.
   Deve restare allineata a data-deadline nelle pagine urban / val-di-chienti. */
const DEADLINES = {
  'Lume Urban':          '2026-09-14T00:00:00+02:00',
  'Lume Val di Chienti': '2026-10-16T12:00:00+02:00',
};

/* Prezzi ufficiali per piano_id, allineati a PLANS in urban.html / val-di-chienti.html.
   Il client manda piano_id + importo/rate solo per comodità di visualizzazione:
   qui si ricontrolla sempre importo/rate contro questa tabella, non ci si fida del body. */
const PIANI = {
  'urb-unica':      { importo: 420, rate: 1 },
  'urb-rate3':      { importo: 450, rate: 3 },
  'mot-unica':      { importo: 510, rate: 1 },
  'mot-rate4':      { importo: 540, rate: 4 },
  'mot-box-unica':  { importo: 750, rate: 1 },
  'mot-box-rate6':  { importo: 810, rate: 6 },
};

function prevenditaChiusa(sede, now) {
  const d = DEADLINES[sede];
  return !!d && (now || Date.now()) >= new Date(d).getTime();
}
exports.prevenditaChiusa = prevenditaChiusa;

/* Token del link riservato alle consulenti (env SEDE_TOKEN, lo stesso che sta
   nel parametro ?k= del link in Airtable). Con token valido il checkout resta
   aperto anche dopo la scadenza: le iscrizioni si chiudono in sede.
   Se SEDE_TOKEN non e impostato nessun token passa e vale solo la scadenza. */
function tokenSedeValido(token) {
  const atteso = process.env.SEDE_TOKEN || '';
  if (!atteso || typeof token !== 'string' || token.length !== atteso.length) return false;
  const crypto = require('crypto');
  return crypto.timingSafeEqual(Buffer.from(token), Buffer.from(atteso));
}
exports.tokenSedeValido = tokenSedeValido;

exports.handler = async function(event) {
  if (event.httpMethod === 'OPTIONS') return { statusCode: 204, headers: CORS, body: '' };
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, headers: CORS, body: JSON.stringify({ ok: false, error: 'Method not allowed' }) };
  }

  try {
    const Stripe = require('stripe');
    const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, { apiVersion: '2024-06-20' });
    const body = JSON.parse(event.body || '{}');
    const { email, nome, cognome, piano_id, sede, page, sede_token } = body;

    if (!email || !piano_id) {
      return { statusCode: 400, headers: CORS, body: JSON.stringify({ ok: false, error: 'email e piano_id obbligatori' }) };
    }

    const piano = PIANI[piano_id];
    if (!piano) {
      return { statusCode: 400, headers: CORS, body: JSON.stringify({ ok: false, error: 'piano_id sconosciuto' }) };
    }

    if (prevenditaChiusa(sede) && !tokenSedeValido(sede_token)) {
      return { statusCode: 410, headers: CORS, body: JSON.stringify({ ok: false, error: 'La prevendita per questa sede è terminata. Richiedi informazioni per verificare la disponibilità.' }) };
    }

    // Redirect URLs dinamici in base alla pagina sorgente (urban / motion / ...)
    const origin = (event.headers.origin || event.headers.referer || '').replace(/\/$/, '');
    const baseUrl = origin || `https://${event.headers.host}`;
    const pageName = (page || 'urban').replace(/[^a-z0-9-]/gi, '');
    const successUrl = `${baseUrl}/${pageName}.html?payment=success&session_id={CHECKOUT_SESSION_ID}`;
    const cancelUrl  = `${baseUrl}/${pageName}.html?payment=cancel`;

    const nomeCompleto = [nome, cognome].filter(Boolean).join(' ');
    const sedeLabel = sede || 'Lume';
    const importoUfficiale = piano.importo;
    const nRate = piano.rate;

    let session;

    if (nRate === 1) {
      // ── Pagamento unico ───────────────────────────────────────────
      session = await stripe.checkout.sessions.create({
        mode: 'payment',
        customer_email: email,
        locale: 'it',
        line_items: [{
          price_data: {
            currency: 'eur',
            product_data: {
              name: `${sedeLabel} — Abbonamento Annuale`,
              description: 'Soluzione unica anticipata',
            },
            unit_amount: Math.round(importoUfficiale * 100),
          },
          quantity: 1,
        }],
        payment_intent_data: {
          metadata: { piano_id, email, nome: nomeCompleto, sede: sedeLabel },
        },
        success_url: successUrl,
        cancel_url: cancelUrl,
      });

    } else {
      // ── Rateizzato: N rate mensili (importo per rata = importo / N) ──
      // n8n gestisce la cancellazione dopo N pagamenti ascoltando
      // l'evento invoice.paid e cancellando la subscription all'Nª rata.
      const perRataCents = Math.round((importoUfficiale / nRate) * 100); // importo per rata, dinamico
      session = await stripe.checkout.sessions.create({
        mode: 'subscription',
        customer_email: email,
        locale: 'it',
        line_items: [{
          price_data: {
            currency: 'eur',
            product_data: {
              name: `${sedeLabel} — Abbonamento Annuale ${nRate} Rate`,
              description: `${nRate} rate mensili da €${Math.round(importoUfficiale / nRate)} · totale €${importoUfficiale}`,
            },
            unit_amount: perRataCents,
            recurring: { interval: 'month', interval_count: 1 },
          },
          quantity: 1,
        }],
        subscription_data: {
          metadata: {
            piano_id,
            email,
            nome: nomeCompleto,
            sede: sedeLabel,
            installments_total: String(nRate),
            installments_paid: '0',
          },
        },
        success_url: successUrl,
        cancel_url: cancelUrl,
      });
    }

    return {
      statusCode: 200,
      headers: CORS,
      body: JSON.stringify({ ok: true, url: session.url }),
    };

  } catch (err) {
    console.error('Stripe create-checkout error:', err.message);
    return {
      statusCode: 500,
      headers: CORS,
      body: JSON.stringify({ ok: false, error: err.message }),
    };
  }
};
