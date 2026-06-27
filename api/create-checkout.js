'use strict';
/**
 * POST /api/create-checkout
 * Crea una Stripe Checkout Session e restituisce l'URL di pagamento.
 * - piano unica  → mode: 'payment',      €360 una tantum
 * - piano rate3  → mode: 'subscription', €130/mese × 3 rate
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
    const { email, nome, cognome, piano_id, importo, rate, sede } = body;

    if (!email || !piano_id) {
      return { statusCode: 400, headers: CORS, body: JSON.stringify({ ok: false, error: 'email e piano_id obbligatori' }) };
    }

    // Determina origin per i redirect URLs
    const origin = (event.headers.origin || event.headers.referer || '').replace(/\/$/, '');
    const baseUrl = origin || `https://${event.headers.host}`;
    const successUrl = `${baseUrl}/urban.html?payment=success&session_id={CHECKOUT_SESSION_ID}`;
    const cancelUrl  = `${baseUrl}/urban.html?payment=cancel`;
    const nomeCompleto = [nome, cognome].filter(Boolean).join(' ');

    let session;

    if (rate === 1) {
      // ── Pagamento unico €360 ──────────────────────────────────────
      session = await stripe.checkout.sessions.create({
        mode: 'payment',
        customer_email: email,
        locale: 'it',
        line_items: [{
          price_data: {
            currency: 'eur',
            product_data: {
              name: 'Lume Urban — Abbonamento Annuale',
              description: 'Soluzione unica anticipata',
            },
            unit_amount: Math.round((importo || 360) * 100),
          },
          quantity: 1,
        }],
        payment_intent_data: {
          metadata: {
            piano_id,
            email,
            nome: nomeCompleto,
            sede: sede || 'Lume Urban',
          },
        },
        success_url: successUrl,
        cancel_url: cancelUrl,
      });

    } else {
      // ── 3 rate da €130/mese ───────────────────────────────────────
      // La subscription viene creata da Stripe al pagamento.
      // n8n gestisce la cancellazione dopo 3 pagamenti ascoltando
      // l'evento invoice.paid e cancellando la subscription alla 3a rata.
      session = await stripe.checkout.sessions.create({
        mode: 'subscription',
        customer_email: email,
        locale: 'it',
        line_items: [{
          price_data: {
            currency: 'eur',
            product_data: {
              name: 'Lume Urban — Abbonamento Annuale 3 Rate',
              description: '3 rate mensili da €130 · totale €390',
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
            sede: sede || 'Lume Urban',
            installments_total: '3',
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
