'use strict';
/**
 * POST /api/register
 * Crea membro + contratto in PerfectGym e inizializza la registrazione carta.
 * Risponde { ok, memberId, contractId, redirectUrl }.
 */
const pg = require('../lib/perfectgym');
const { validateInput, buildContractMemberPayload } = require('../lib/mapper');

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': process.env.ALLOWED_ORIGIN || '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Content-Type': 'application/json',
};

exports.handler = async function(event) {
  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers: CORS_HEADERS, body: '' };
  }
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, headers: CORS_HEADERS, body: JSON.stringify({ ok: false, error: 'Method not allowed' }) };
  }

  try {
    const input = JSON.parse(event.body || '{}');

    const errors = validateInput(input);
    if (errors.length) {
      return { statusCode: 400, headers: CORS_HEADERS, body: JSON.stringify({ ok: false, error: 'Dati non validi', details: errors }) };
    }

    const payload = buildContractMemberPayload(input, { startDate: process.env.CONTRACT_START_DATE || undefined });
    const created = await pg.addContractMember(payload);
    const memberId = created && (created.memberId || created.MemberId);
    const contractId = created && (created.contractId || created.ContractId);
    if (!memberId) {
      return { statusCode: 502, headers: CORS_HEADERS, body: JSON.stringify({ ok: false, error: 'PerfectGym non ha restituito memberId', raw: created }) };
    }

    let redirectUrl = null;
    try {
      const thankYou = process.env.THANK_YOU_URL || undefined;
      const cc = await pg.initCreditCardRegistration({ memberId, thankYouPageUrl: thankYou });
      redirectUrl = cc && (cc.url || cc.Url) || null;
    } catch (ccErr) {
      return { statusCode: 207, headers: CORS_HEADERS, body: JSON.stringify({
        ok: true, memberId, contractId, redirectUrl: null,
        warning: 'Membro e contratto creati, ma inizializzazione carta fallita: ' + ccErr.message,
      })};
    }

    return { statusCode: 200, headers: CORS_HEADERS, body: JSON.stringify({ ok: true, memberId, contractId, redirectUrl }) };
  } catch (err) {
    const status = err.status && err.status >= 400 && err.status < 600 ? err.status : 500;
    return { statusCode: status, headers: CORS_HEADERS, body: JSON.stringify({ ok: false, error: err.message, details: err.body || null }) };
  }
};
