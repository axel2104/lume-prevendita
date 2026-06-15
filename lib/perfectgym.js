'use strict';
/**
 * Client API PerfectGym — write API REST v2.2.
 * Auth: header X-Client-Id / X-Client-Secret (le stesse credenziali della dashboard).
 * Docs: <istanza>/Api/Docs/ApiReference/Index.html
 *
 * NB: usa fetch globale (Node >= 18, default su Vercel).
 */

const PG_API_BASE = (process.env.PG_API_BASE || 'https://lumefitness.perfectgym.com/Api').replace(/\/+$/, '');

function headers() {
  const id = process.env.PG_CLIENT_ID;
  const secret = process.env.PG_CLIENT_SECRET;
  if (!id || !secret) {
    throw new Error('Credenziali PerfectGym mancanti: imposta PG_CLIENT_ID e PG_CLIENT_SECRET.');
  }
  return {
    'X-Client-Id': id,
    'X-Client-Secret': secret,
    'Accept': 'application/json',
    'Content-Type': 'application/json',
  };
}

async function pgRequest(method, path, body) {
  const url = PG_API_BASE + path;
  const res = await fetch(url, {
    method,
    headers: headers(),
    body: body != null ? JSON.stringify(body) : undefined,
  });
  const text = await res.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch (_) { data = text; }
  if (!res.ok) {
    const msg = (data && (data.Message || data.message || data.error)) || text || ('HTTP ' + res.status);
    const err = new Error('PerfectGym ' + method + ' ' + path + ' -> ' + res.status + ': ' + msg);
    err.status = res.status;
    err.body = data;
    throw err;
  }
  return data;
}

function addContractMember({ paymentPlanId, homeClubId, signUpDate, startDate, personalData, addressData }) {
  return pgRequest('POST', '/v2.2/Members/AddContractMember', {
    contractData: { paymentPlanId, signUpDate, startDate },
    homeClubId,
    personalData,
    addressData,
  });
}

function addGuestMember({ homeClubId, personalData, addressData }) {
  return pgRequest('POST', '/v2.2/Members/AddGuestMember', { homeClubId, personalData, addressData });
}

function initCreditCardRegistration({ memberId, thankYouPageUrl, assignToContractsMode }) {
  return pgRequest('POST', '/v2.2/CreditCards/InitExternalCreditCardRegistration', {
    userId: memberId,
    thankYouPageUrl: thankYouPageUrl || undefined,
    assignToContractsMode: assignToContractsMode || 'AssignToAllActiveContracts',
  });
}

function addDirectDebit({ memberId, accountNumber, ownerName, countryCode, contractId, setAsDefault }) {
  return pgRequest('POST', '/v2.2/MemberPaymentSource/AddDirectDebitPaymentMethod', {
    memberId,
    accountNumber,
    ownerName,
    countryCode,
    contractId,
    setAsDefault: setAsDefault !== false,
  });
}

async function listPaymentPlans(clubId) {
  let path = '/v2.2/odata/PaymentPlans?$select=id,name,defaultPriceGross,clubId,isDeleted&$top=500';
  if (clubId != null) path += '&$filter=' + encodeURIComponent('clubId eq ' + clubId + ' and isDeleted eq false');
  const data = await pgRequest('GET', path);
  return (data && data.value) || [];
}

module.exports = {
  PG_API_BASE,
  pgRequest,
  addContractMember,
  addGuestMember,
  initCreditCardRegistration,
  addDirectDebit,
  listPaymentPlans,
};
'use strict';
/**
 * Client API PerfectGym — write API REST v2.2.
 * Auth: header X-Client-Id / X-Client-Secret (le stesse credenziali della dashboard).
 * Docs: <istanza>/Api/Docs/ApiReference/Index.html
 *
 * NB: usa fetch globale (Node >= 18, default su Vercel).
 */

const PG_API_BASE = (process.env.PG_API_BASE || 'https://lumefitness.perfectgym.com/Api').replace(/\/+$/, '');

function headers() {
  const id = process.env.PG_CLIENT_ID;
  const secret = process.env.PG_CLIENT_SECRET;
  if (!id || !secret) {
    throw new Error('Credenziali PerfectGym mancanti: imposta PG_CLIENT_ID e PG_CLIENT_SECRET.');
  }
  return {
    'X-Client-Id': id,
    'X-Client-Secret': secret,
    'Accept': 'application/json',
    'Content-Type': 'application/json',
  };
}

async function pgRequest(method, path, body) {
  const url = PG_API_BASE + path;
  const res = await fetch(url, {
    method,
    headers: headers(),
    body: body != null ? JSON.stringify(body) : undefined,
  });
  const text = await res.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch (_) { data = text; }
  if (!res.ok) {
    const msg = (data && (data.Message || data.message || data.error)) || text || ('HTTP ' + res.status);
    const err = new Error('PerfectGym ' + method + ' ' + path + ' -> ' + res.status + ': ' + msg);
    err.status = res.status;
    err.body = data;
    throw err;
  }
  return data;
}

function addContractMember({ paymentPlanId, homeClubId, signUpDate, startDate, personalData, addressData }) {
  return pgRequest('POST', '/v2.2/Members/AddContractMember', {
    contractData: { paymentPlanId, signUpDate, startDate },
    homeClubId,
    personalData,
    addressData,
  });
}

function addGuestMember({ homeClubId, personalData, addressData }) {
  return pgRequest('POST', '/v2.2/Members/AddGuestMember', { homeClubId, personalData, addressData });
}

function initCreditCardRegistration({ memberId, thankYouPageUrl, assignToContractsMode }) {
  return pgRequest('POST', '/v2.2/CreditCards/InitExternalCreditCardRegistration', {
    userId: memberId,
    thankYouPageUrl: thankYouPageUrl || undefined,
    assignToContractsMode: assignToContractsMode || 'AssignToAllActiveContracts',
  });
}

function addDirectDebit({ memberId, accountNumber, ownerName, countryCode, contractId, setAsDefault }) {
  return pgRequest('POST', '/v2.2/MemberPaymentSource/AddDirectDebitPaymentMethod', {
    memberId, accountNumber, ownerName, countryCode, contractId,
    setAsDefault: setAsDefault !== false,
  });
}

async function listPaymentPlans(clubId) {
  let path = '/v2.2/odata/PaymentPlans?$select=id,name,defaultPriceGross,clubId,isDeleted&$top=500';
  if (clubId != null) path += '&$filter=' + encodeURIComponent('clubId eq ' + clubId + ' and isDeleted eq false');
  const data = await pgRequest('GET', path);
  return (data && data.value) || [];
}

module.exports = {
  PG_API_BASE, pgRequest, addContractMember, addGuestMember,
  initCreditCardRegistration, addDirectDebit, listPaymentPlans,
};
