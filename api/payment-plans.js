'use strict';
/**
 * GET /api/payment-plans?clubId=2
 * Helper di configurazione: elenca i Payment Plan di un club per trovare i pgPaymentPlanId
 * da inserire nel frontend. Proteggi/rimuovi questo endpoint in produzione.
 */
const pg = require('../lib/perfectgym');

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': process.env.ALLOWED_ORIGIN || '*',
  'Content-Type': 'application/json',
};

exports.handler = async function(event) {
  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers: CORS_HEADERS, body: '' };
  }

  try {
    const params = event.queryStringParameters || {};
    if (process.env.ADMIN_KEY && params.key !== process.env.ADMIN_KEY) {
      return { statusCode: 401, headers: CORS_HEADERS, body: JSON.stringify({ ok: false, error: 'unauthorized' }) };
    }
    const clubId = params.clubId != null ? Number(params.clubId) : undefined;
    const plans = await pg.listPaymentPlans(clubId);
    return { statusCode: 200, headers: CORS_HEADERS, body: JSON.stringify({ ok: true, count: plans.length, plans }) };
  } catch (err) {
    return { statusCode: err.status || 500, headers: CORS_HEADERS, body: JSON.stringify({ ok: false, error: err.message }) };
  }
};
