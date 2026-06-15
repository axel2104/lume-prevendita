'use strict';
/**
 * Validazione + mapping dal payload del form allo schema PerfectGym.
 * Funzioni pure (no rete) → facilmente testabili.
 */

const SEX_MAP = { F: 'Female', M: 'Male', X: 'Other' };

function isEmail(v) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v || ''); }
function isPhone(v) { return /^[+]?[\d\s().-]{7,20}$/.test(v || ''); }
function isCF(v) { return /^[A-Z0-9]{16}$/.test((v || '').toUpperCase()); }

/** Ritorna array di errori (vuoto = valido). */
function validateInput(input) {
  const e = [];
  if (!input || typeof input !== 'object') return ['payload mancante'];
  const m = input.member || {};
  if (!m.firstName) e.push('member.firstName mancante');
  if (!m.lastName) e.push('member.lastName mancante');
  if (!isEmail(m.email)) e.push('member.email non valida');
  if (!isPhone(m.phone)) e.push('member.phone non valido');
  if (!m.birthDate) e.push('member.birthDate mancante');
  if (!SEX_MAP[m.gender]) e.push('member.gender non valido (F|M|X)');
  if (!isCF(m.fiscalCode)) e.push('member.fiscalCode (codice fiscale) non valido');
  const plan = input.plan || {};
  if (plan.pgPaymentPlanId == null || plan.pgPaymentPlanId === '') {
    e.push('plan.pgPaymentPlanId mancante (configura l\'ID del Payment Plan PerfectGym)');
  }
  const club = input.club || {};
  if (club.pgClubId == null) e.push('club.pgClubId mancante');
  if (!(input.consents && input.consents.privacy && input.consents.terms)) {
    e.push('consensi privacy/termini obbligatori non accettati');
  }
  return e;
}

/** yyyy-mm-dd → ISO date-time UTC a mezzanotte. */
function toIsoDate(d) {
  if (!d) return undefined;
  if (/^\d{4}-\d{2}-\d{2}$/.test(d)) return d + 'T00:00:00Z';
  return new Date(d).toISOString();
}

/** Costruisce il body per AddContractMember. */
function buildContractMemberPayload(input, opts = {}) {
  const m = input.member || {};
  const now = (opts.now ? new Date(opts.now) : new Date());
  const nowIso = now.toISOString();
  const country = input.countrySymbol || 'IT';
  return {
    paymentPlanId: Number(input.plan.pgPaymentPlanId),
    homeClubId: Number(input.club.pgClubId),
    signUpDate: nowIso,
    startDate: opts.startDate ? toIsoDate(opts.startDate) : nowIso,
    personalData: {
      firstName: m.firstName,
      lastName: m.lastName,
      email: m.email,
      phoneNumber: m.phone,
      birthDate: toIsoDate(m.birthDate),
      sex: SEX_MAP[m.gender],
      personalId: (m.fiscalCode || '').toUpperCase(),   // codice fiscale
      citizenshipCountrySymbol: country,
    },
    addressData: {
      cityName: m.city || undefined,
      countrySymbol: country,
    },
  };
}

module.exports = { SEX_MAP, isEmail, isPhone, isCF, validateInput, toIsoDate, buildContractMemberPayload };
