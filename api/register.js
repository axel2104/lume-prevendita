'use strict';
/**
 * POST /api/register
 * Crea membro + contratto in PerfectGym e inizializza la registrazione carta.
 * Risponde { ok, memberId, contractId, redirectUrl }.
 */
const pg = require('../lib/perfectgym');
const { validateInput, buildContractMemberPayload } = require('../lib/mapper');

function setCors(res) {
  const origin = process.env.ALLOWED_ORIGIN || '*';
  res.setHeader('Access-Control-Allow-Origin', origin);
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

module.exports = async function handler(req, res) {
  setCors(res);
  if (req.method === 'OPTIONS') { res.status(204).end(); return; }
  if (req.method !== 'POST') { res.status(405).json({ ok: false, error: 'Method not allowed' }); return; }

  try {
    const input = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});

    // 1) validazione server-side
    const errors = validateInput(input);
    if (errors.length) { res.status(400).json({ ok: false, error: 'Dati non validi', details: errors }); return; }

    // 2) crea membro + contratto
    const payload = buildContractMemberPayload(input, { startDate: process.env.CONTRACT_START_DATE || undefined });
    const created = await pg.addContractMember(payload);
    const memberId = created && (created.memberId || created.MemberId);
    const contractId = created && (created.contractId || created.ContractId);
    if (!memberId) { res.status(502).json({ ok: false, error: 'PerfectGym non ha restituito memberId', raw: created }); return; }

    // 3) inizializza registrazione carta (acconto/prima rata sul Payment Plan)
    let redirectUrl = null;
    try {
      const thankYou = process.env.THANK_YOU_URL || undefined;
      const cc = await pg.initCreditCardRegistration({ memberId, thankYouPageUrl: thankYou });
      redirectUrl = cc && (cc.url || cc.Url) || null;
    } catch (ccErr) {
      res.status(207).json({
        ok: true, memberId, contractId, redirectUrl: null,
        warning: 'Membro e contratto creati, ma inizializzazione carta fallita: ' + ccErr.message,
      });
      return;
    }

    res.status(200).json({ ok: true, memberId, contractId, redirectUrl });
  } catch (err) {
    const status = err.status && err.status >= 400 && err.status < 600 ? err.status : 500;
    res.status(status).json({ ok: false, error: err.message, details: err.body || null });
  }
};
