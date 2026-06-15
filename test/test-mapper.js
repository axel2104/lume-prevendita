'use strict';
const assert = require('assert');
const { validateInput, buildContractMemberPayload } = require('../lib/mapper');

let pass = 0, fail = 0;
function t(name, fn) { try { fn(); pass++; console.log('  ok  ' + name); } catch (e) { fail++; console.log('FAIL  ' + name + '\n      ' + e.message); } }

const good = {
  club: { id: 'macerata', pgClubId: 2, name: 'Lume Macerata' },
  plan: { id: 'mac-unica', name: 'Annuale', total: 360, installments: 1, pgPaymentPlanId: 1234 },
  member: { firstName: 'Mario', lastName: 'Rossi', email: 'mario@example.com', phone: '+39 333 1234567',
            birthDate: '1990-05-21', gender: 'M', fiscalCode: 'RSSMRA90E21D451K', city: 'Macerata' },
  countrySymbol: 'IT',
  consents: { privacy: true, terms: true, mkt: false },
  deposit: 50,
};

t('payload valido → nessun errore', () => assert.deepStrictEqual(validateInput(good), []));

t('email non valida → errore', () => {
  const bad = JSON.parse(JSON.stringify(good)); bad.member.email = 'nope';
  assert.ok(validateInput(bad).some(e => /email/.test(e)));
});

t('codice fiscale non valido → errore', () => {
  const bad = JSON.parse(JSON.stringify(good)); bad.member.fiscalCode = '123';
  assert.ok(validateInput(bad).some(e => /fiscale/.test(e)));
});

t('pgPaymentPlanId mancante → errore', () => {
  const bad = JSON.parse(JSON.stringify(good)); bad.plan.pgPaymentPlanId = null;
  assert.ok(validateInput(bad).some(e => /pgPaymentPlanId/.test(e)));
});

t('consensi mancanti → errore', () => {
  const bad = JSON.parse(JSON.stringify(good)); bad.consents.terms = false;
  assert.ok(validateInput(bad).some(e => /consensi/.test(e)));
});

t('build payload: struttura e mapping corretti', () => {
  const p = buildContractMemberPayload(good, { now: '2026-06-15T10:00:00Z' });
  assert.strictEqual(p.homeClubId, 2);
  assert.strictEqual(p.paymentPlanId, 1234);
  assert.strictEqual(p.signUpDate, '2026-06-15T10:00:00.000Z');
  assert.strictEqual(p.startDate, '2026-06-15T10:00:00.000Z');
  assert.strictEqual(p.personalData.sex, 'Male');
  assert.strictEqual(p.personalData.personalId, 'RSSMRA90E21D451K');
  assert.strictEqual(p.personalData.birthDate, '1990-05-21T00:00:00Z');
  assert.strictEqual(p.personalData.phoneNumber, '+39 333 1234567');
  assert.strictEqual(p.personalData.citizenshipCountrySymbol, 'IT');
  assert.strictEqual(p.addressData.countrySymbol, 'IT');
  assert.strictEqual(p.addressData.cityName, 'Macerata');
});

t('gender F → Female, X → Other', () => {
  const f = JSON.parse(JSON.stringify(good)); f.member.gender = 'F';
  assert.strictEqual(buildContractMemberPayload(f).personalData.sex, 'Female');
  const x = JSON.parse(JSON.stringify(good)); x.member.gender = 'X';
  assert.strictEqual(buildContractMemberPayload(x).personalData.sex, 'Other');
});

t('startDate fissa rispettata', () => {
  const p = buildContractMemberPayload(good, { now: '2026-06-15T10:00:00Z', startDate: '2026-09-01' });
  assert.strictEqual(p.startDate, '2026-09-01T00:00:00Z');
});

console.log('\n' + pass + ' passati, ' + fail + ' falliti');
process.exit(fail ? 1 : 0);
