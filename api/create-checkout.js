'use strict';
/**
 * POST /api/create-checkout
 * Crea una Stripe Checkout Session e restituisce l'URL di pagamento.
 * - rate === 1  → mode: 'payment',      importo unico
 * - rate > 1   → mode: 'subscription', €130/mese × N rate
 *
 * Body params:
 *   email, nome, cognome, piano_id, importo, rate, sede, page
 *
 * Env vars richieste:
 *   STRIPE_SECRET_KEY   — secret key Stripe (sk_live_... / sk_test_...)
 *   ALLOWED_ORIGIN      — opzionale, default '*'
 */
const Stripe = require('stripe');

const CORS = {
  'Access-Control-Allow-Origin': process.env.ALLOWED_ORIGIN || '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Content-Type': 'application/json',
};

exports.handler = async function(event) {
  if (event.httpMethod === 'OPTIONS') return { statusCode: 204, headers: CORS, body: '' };
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, headers: CORS, body: JSON.stringify({ ok: false, error: 'Method not allowed' }) };
  }

  try {
    const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, { apiVersion: '2024-06-20' });
    const body = JSON.parse(event.body || '{}');
    const { email, nome, cognome, piano_id, importo, rate, sede, page } = body;

    if (!email || !piano_id) {
      return { statusCode: 400, headers: CORS, body: JSON.stringify({ ok: false, error: 'email e piano_id obbligatori' }) };
    }

    // Redirect URLs dinamici in base alla pagina sorgente (urban / motion / ...)
    const origin = (event.headers.origin || event.headers.referer || '').replace(/\/$/, '');
    const baseUrl = origin || `https://${event.headers.host}`;
    const pageName = (page || 'urban').replace(/[^a-z0-9-]/gi, '');
    const successUrl = `${baseUrl}/${pageName}.html?payment=success&session_id={CHECKOUT_SESSION_ID}`;
    const cancelUrl  = `${baseUrl}/${pageName}.html?payment=cancel`;

    const nomeCompleto = [nome, cognome].filter(Boolean).join(' ');
    const sedeLabel = sede || 'Lume';
    const nRate = Number(rate) || 1;

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
            unit_amount: Math.round((importo || 0) * 100),
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
      // ── Rateizzato: N rate da €130/mese ──────────────────────────
      // n8n gestisce la cancellazione dopo N pagamenti ascoltando
      // l'evento invoice.paid e cancellando la subscription all'Nª rata.
      session = await stripe.checkout.sessions.create({
        mode: 'subscription',
        customer_email: email,
        locale: 'it',
        line_items: [{
          price_data: {
            currency: 'eur',
            product_data: {
              name: `${sedeLabel} — Abbonamento Annuale ${nRate} Rate`,
              description: `${nRate} rate mensili da €130 · totale €${importo || nRate * 130}`,
            },
            unit_amount: 13000, // €130 in centesimi
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
