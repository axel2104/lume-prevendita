'use strict';
/**
 * GET /api/payment-plans?clubId=2
 * Helper di configurazione: elenca i Payment Plan di un club per trovare i pgPaymentPlanId
 * da inserire nel frontend. Proteggi/rimuovi questo endpoint in produzione.
 */
const pg = require('../lib/perfectgym');

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', process.env.ALLOWED_ORIGIN || '*');
  try {
    if (process.env.ADMIN_KEY && (req.query.key !== process.env.ADMIN_KEY)) {
      res.status(401).json({ ok: false, error: 'unauthorized' }); return;
    }
    const clubId = req.query.clubId != null ? Number(req.query.clubId) : undefined;
    const plans = await pg.listPaymentPlans(clubId);
    res.status(200).json({ ok: true, count: plans.length, plans });
  } catch (err) {
    res.status(err.status || 500).json({ ok: false, error: err.message });
  }
};
