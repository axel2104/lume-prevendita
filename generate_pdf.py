#!/usr/bin/env python3
"""Generate Lume Fitness — Documentazione Flow Prevendita PDF"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# ── Colori brand Lume ────────────────────────────────────────────────────────
NERO    = colors.HexColor('#1a1a1a')
GIALLO  = colors.HexColor('#F5C518')  # brand accent
GRIGIO  = colors.HexColor('#4a4a4a')
GRIGIO_L= colors.HexColor('#f5f5f5')
GRIGIO_M= colors.HexColor('#cccccc')
BIANCO  = colors.white

W, H = A4

# ── Stili ────────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def style(name, **kw):
    base = styles.get(name, styles['Normal'])
    ps = ParagraphStyle(
        name + '_custom_' + str(id(kw)),
        parent=base,
        **kw
    )
    return ps

S_cover_title = style('Title',
    fontSize=32, textColor=BIANCO, leading=40,
    alignment=TA_CENTER, fontName='Helvetica-Bold')

S_cover_sub = style('Normal',
    fontSize=14, textColor=GIALLO, leading=20,
    alignment=TA_CENTER, fontName='Helvetica')

S_cover_meta = style('Normal',
    fontSize=10, textColor=GRIGIO_M, leading=14,
    alignment=TA_CENTER, fontName='Helvetica')

S_section = style('Heading1',
    fontSize=18, textColor=NERO, leading=24,
    fontName='Helvetica-Bold', spaceAfter=6, spaceBefore=18)

S_h2 = style('Heading2',
    fontSize=13, textColor=GRIGIO, leading=18,
    fontName='Helvetica-Bold', spaceAfter=4, spaceBefore=12)

S_h3 = style('Heading3',
    fontSize=11, textColor=NERO, leading=15,
    fontName='Helvetica-Bold', spaceAfter=3, spaceBefore=8)

S_body = style('Normal',
    fontSize=10, textColor=NERO, leading=15,
    fontName='Helvetica', alignment=TA_JUSTIFY)

S_body_center = style('Normal',
    fontSize=10, textColor=NERO, leading=15,
    fontName='Helvetica', alignment=TA_CENTER)

S_bullet = style('Normal',
    fontSize=10, textColor=NERO, leading=15,
    fontName='Helvetica', leftIndent=14, firstLineIndent=-10)

S_small = style('Normal',
    fontSize=8.5, textColor=GRIGIO, leading=12, fontName='Helvetica')

S_code = style('Normal',
    fontSize=8.5, textColor=colors.HexColor('#333333'), leading=13,
    fontName='Courier', backColor=GRIGIO_L, leftIndent=8, rightIndent=8,
    borderPadding=6)

S_label = style('Normal',
    fontSize=9, textColor=BIANCO, leading=12,
    fontName='Helvetica-Bold', alignment=TA_CENTER)

S_table_head = style('Normal',
    fontSize=9, textColor=BIANCO, leading=12,
    fontName='Helvetica-Bold', alignment=TA_CENTER)

S_table_cell = style('Normal',
    fontSize=9, textColor=NERO, leading=13,
    fontName='Helvetica')

S_footer = style('Normal',
    fontSize=8, textColor=GRIGIO_M, leading=10,
    fontName='Helvetica', alignment=TA_CENTER)


# ── Helper: box colorato ─────────────────────────────────────────────────────
def badge(txt, bg=GIALLO, fg=NERO, width=60*mm):
    data = [[Paragraph(txt, style('Normal', fontSize=8, textColor=fg,
                                  fontName='Helvetica-Bold', alignment=TA_CENTER))]]
    t = Table(data, colWidths=[width], rowHeights=[14])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg),
        ('ROUNDEDCORNERS', [4]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    return t


def hr():
    return HRFlowable(width='100%', thickness=1, color=GRIGIO_M, spaceAfter=8, spaceBefore=4)


def step_table(steps):
    """Render a numbered step list as a styled table."""
    rows = []
    for i, (num, title, desc) in enumerate(steps):
        rows.append([
            Paragraph(num, style('Normal', fontSize=13, textColor=GIALLO,
                                 fontName='Helvetica-Bold', alignment=TA_CENTER)),
            Paragraph(f'<b>{title}</b><br/><font size=9 color="#4a4a4a">{desc}</font>',
                      style('Normal', fontSize=10, textColor=NERO,
                            fontName='Helvetica', leading=14))
        ])
    t = Table(rows, colWidths=[18*mm, 140*mm])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LINEBELOW', (0,0), (-1,-2), 0.5, GRIGIO_M),
        ('BACKGROUND', (0,0), (0,-1), NERO),
        ('BACKGROUND', (1,0), (1,-1), GRIGIO_L),
        ('LEFTPADDING', (1,0), (1,-1), 10),
    ]))
    return t


def webhook_table(rows_data):
    header = [
        Paragraph('Webhook', S_table_head),
        Paragraph('URL', S_table_head),
        Paragraph('Trigger', S_table_head),
        Paragraph('Azione n8n', S_table_head),
    ]
    rows = [header] + [
        [Paragraph(c, S_table_cell) for c in row]
        for row in rows_data
    ]
    t = Table(rows, colWidths=[32*mm, 58*mm, 35*mm, 35*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NERO),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [BIANCO, GRIGIO_L]),
        ('GRID', (0,0), (-1,-1), 0.5, GRIGIO_M),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    return t


def two_col_table(left, right, w_left=80*mm, w_right=78*mm):
    t = Table([[left, right]], colWidths=[w_left, w_right], hAlign='LEFT')
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    return t


# ── Cover page ───────────────────────────────────────────────────────────────
def cover_page():
    items = []
    # Blocco nero
    cover_data = [[
        Paragraph('LUME FITNESS', style('Normal', fontSize=11, textColor=GIALLO,
                                        fontName='Helvetica-Bold', alignment=TA_CENTER,
                                        spaceAfter=6)),
        Paragraph(' ', S_cover_title),  # spacer interno
        Paragraph('Sistema di Prevendita &amp; Promozioni', S_cover_title),
        Paragraph(' ', S_cover_sub),
        Paragraph('Documentazione tecnica e di processo', S_cover_sub),
        Paragraph(' ', S_cover_meta),
        Paragraph('promo.lumefitness.it   •   Giugno 2026', S_cover_meta),
    ]]

    # Simulo una cover con un grande table colorato
    cover_content = [
        Spacer(1, 30*mm),
        Paragraph('LUME FITNESS', style('Normal', fontSize=12, textColor=GIALLO,
                                        fontName='Helvetica-Bold', alignment=TA_CENTER)),
        Spacer(1, 8*mm),
        Paragraph('Sistema di Prevendita<br/>&amp; Promozioni', style('Normal',
            fontSize=28, textColor=BIANCO, fontName='Helvetica-Bold',
            alignment=TA_CENTER, leading=36)),
        Spacer(1, 6*mm),
        Paragraph('Documentazione tecnica e di processo', style('Normal',
            fontSize=13, textColor=GIALLO, fontName='Helvetica',
            alignment=TA_CENTER)),
        Spacer(1, 14*mm),
        Paragraph('promo.lumefitness.it', style('Normal',
            fontSize=10, textColor=GRIGIO_M, fontName='Helvetica',
            alignment=TA_CENTER)),
        Paragraph('Giugno 2026', style('Normal',
            fontSize=10, textColor=GRIGIO_M, fontName='Helvetica',
            alignment=TA_CENTER)),
    ]

    big_table = Table([[cover_content]], colWidths=[160*mm], rowHeights=[130*mm])
    big_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NERO),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 20),
        ('RIGHTPADDING', (0,0), (-1,-1), 20),
    ]))
    items.append(big_table)
    items.append(Spacer(1, 10*mm))

    # Riquadro sommario sedi
    sedi_data = [
        [Paragraph('<b>Sede</b>', S_table_head),
         Paragraph('<b>Tipo</b>', S_table_head),
         Paragraph('<b>Stato</b>', S_table_head),
         Paragraph('<b>Apertura</b>', S_table_head)],
        [Paragraph('Lume HQ', S_table_cell),
         Paragraph('Guest Pass 7 gg', S_table_cell),
         Paragraph('Attiva', S_table_cell),
         Paragraph('Macerata', S_table_cell)],
        [Paragraph('Lume Balance', S_table_cell),
         Paragraph('Guest Pass 7 gg', S_table_cell),
         Paragraph('Attiva', S_table_cell),
         Paragraph('Montecassiano', S_table_cell)],
        [Paragraph('Lume Urban', S_table_cell),
         Paragraph('Prevendita Early Bird', S_table_cell),
         Paragraph('Pre-apertura', S_table_cell),
         Paragraph('Set 2026 — Macerata CS', S_table_cell)],
        [Paragraph('Lume Motion', S_table_cell),
         Paragraph('Prevendita Early Bird', S_table_cell),
         Paragraph('Pre-apertura', S_table_cell),
         Paragraph('Ott 2026 — CC Val di Chienti', S_table_cell)],
    ]
    t = Table(sedi_data, colWidths=[38*mm, 46*mm, 30*mm, 46*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NERO),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [BIANCO, GRIGIO_L]),
        ('GRID', (0,0), (-1,-1), 0.5, GRIGIO_M),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    items.append(t)
    return items


# ── Corpo documento ──────────────────────────────────────────────────────────
def build_story():
    story = cover_page()
    story.append(PageBreak())

    # ── 1. Panoramica ────────────────────────────────────────────────────────
    story.append(Paragraph('1. Panoramica del Sistema', S_section))
    story.append(hr())
    story.append(Paragraph(
        'Il portale <b>promo.lumefitness.it</b> centralizza le attività promozionali '
        'di Lume Fitness su un unico sottodominio statico, ospitato su <b>Netlify</b>. '
        'Ogni sede dispone di una pagina dedicata con flow autonomo, integrazioni '
        'n8n, Stripe, Airtable e SendGrid.',
        S_body))
    story.append(Spacer(1, 4*mm))

    # Architettura
    story.append(Paragraph('Stack tecnologico', S_h2))
    arch_data = [
        [Paragraph('<b>Livello</b>', S_table_head),
         Paragraph('<b>Tecnologia</b>', S_table_head),
         Paragraph('<b>Ruolo</b>', S_table_head)],
        [Paragraph('Frontend', S_table_cell),
         Paragraph('HTML/CSS/JS vanilla', S_table_cell),
         Paragraph('Form multi-step, firma digitale Canvas API', S_table_cell)],
        [Paragraph('Hosting', S_table_cell),
         Paragraph('Netlify', S_table_cell),
         Paragraph('CDN + Serverless Function (Stripe)', S_table_cell)],
        [Paragraph('Pagamenti', S_table_cell),
         Paragraph('Stripe Checkout', S_table_cell),
         Paragraph('Pagamento unico e rateizzato (subscription)', S_table_cell)],
        [Paragraph('Automazione', S_table_cell),
         Paragraph('n8n (lumeflow.it)', S_table_cell),
         Paragraph('Webhooks, PDF, email, Airtable', S_table_cell)],
        [Paragraph('CRM', S_table_cell),
         Paragraph('Airtable', S_table_cell),
         Paragraph('Tracking lead, contratti, pagamenti', S_table_cell)],
        [Paragraph('Email', S_table_cell),
         Paragraph('SendGrid', S_table_cell),
         Paragraph('Invio contratto firmato post-pagamento', S_table_cell)],
        [Paragraph('PDF', S_table_cell),
         Paragraph('Gotenberg (self-hosted)', S_table_cell),
         Paragraph('Conversione HTML contratto → PDF', S_table_cell)],
    ]
    arch_t = Table(arch_data, colWidths=[30*mm, 46*mm, 84*mm])
    arch_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NERO),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [BIANCO, GRIGIO_L]),
        ('GRID', (0,0), (-1,-1), 0.5, GRIGIO_M),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(arch_t)
    story.append(PageBreak())

    # ── 2. Flow Guest Pass ───────────────────────────────────────────────────
    story.append(Paragraph('2. Flow — Guest Pass 7 Giorni', S_section))
    story.append(Paragraph('Sedi attive: Lume HQ (Macerata) &amp; Lume Balance (Montecassiano)', S_h2))
    story.append(hr())
    story.append(Paragraph(
        'Promozione dedicata alle sedi operative. L\'utente compila un form '
        'per ricevere un pass gratuito di 7 giorni da provare in struttura.',
        S_body))
    story.append(Spacer(1, 4*mm))

    guest_steps = [
        ('1', 'Selezione sede', 'L\'utente sceglie HQ o Balance dalla landing page index.html'),
        ('2', 'Compilazione form', 'Nome, cognome, email, telefono, comune — promo.html'),
        ('3', 'Verifica iscritto', 'Webhook n8n verifica-iscritto: controlla se già cliente nel gestionale'),
        ('3a', 'Già iscritto', 'Step 6 — Pagina bloccata: "Contattaci a macerata@lumefitness.it"'),
        ('3b', 'Non iscritto', 'Procede al rilascio del pass'),
        ('4', 'Invio dati', 'Webhook n8n iscrizione: salva lead su Airtable con status "In attesa"'),
        ('5', 'Conferma', 'L\'utente riceve email con il codice/link Guest Pass'),
    ]
    story.append(step_table(guest_steps))
    story.append(Spacer(1, 6*mm))
    story.append(PageBreak())

    # ── 3. Flow Prevendita ───────────────────────────────────────────────────
    story.append(Paragraph('3. Flow — Prevendita Early Bird', S_section))
    story.append(Paragraph('Lume Urban (Set 2026) &amp; Lume Motion (Ott 2026)', S_h2))
    story.append(hr())
    story.append(Paragraph(
        'Flow completo di pre-iscrizione per le due nuove sedi. '
        'L\'utente sceglie il piano, firma un contratto digitale e paga tramite Stripe. '
        'Il contratto viene generato come PDF e inviato via email solo dopo la conferma del pagamento.',
        S_body))
    story.append(Spacer(1, 5*mm))

    presale_steps = [
        ('1', 'Pagina sede', 'Descrizione della struttura, benefit e data di apertura'),
        ('2', 'Selezione piano', 'Utente sceglie l\'abbonamento (soluzione unica o rateizzata)'),
        ('3', 'Dati personali', 'Nome, cognome, CF, email, telefono, comune, data di nascita\n(+ dati genitore se minorenne)'),
        ('4', 'Verifica iscritto', 'Webhook verifica-iscritto → proceed:true / proceed:false'),
        ('4a', 'proceed:false', 'Step 6 — Blocco: "Non è possibile procedere online, contattaci"'),
        ('4b', 'proceed:true', 'Airtable: lead salvato con status "In attesa"'),
        ('5', 'Firma contratto', 'Contratto HTML generato, firma digitale su Canvas,\nWebhook FIRMA-CONTRATTO → Airtable: "Contratto firmato"'),
        ('6', 'Pagamento Stripe', 'Redirect a Stripe Checkout (pagamento unico o subscription)'),
        ('7', 'Conferma', 'Stripe redirect su ?payment=success\nWebhook conferma-stripe → Airtable: "Pagamento completato" + session_id'),
        ('8', 'Email contratto', 'n8n genera PDF via Gotenberg, lo salva su Airtable,\ninvia email all\'iscritto con contratto allegato'),
    ]
    story.append(step_table(presale_steps))
    story.append(PageBreak())

    # ── 4. Piani abbonamento ─────────────────────────────────────────────────
    story.append(Paragraph('4. Piani di Abbonamento', S_section))
    story.append(hr())

    # Urban
    story.append(Paragraph('Lume Urban', S_h2))
    urban_data = [
        [Paragraph('<b>Piano</b>', S_table_head),
         Paragraph('<b>Prezzo</b>', S_table_head),
         Paragraph('<b>Modalità</b>', S_table_head),
         Paragraph('<b>Stripe mode</b>', S_table_head)],
        [Paragraph('Soluzione Unica', S_table_cell),
         Paragraph('€360', S_table_cell),
         Paragraph('1 pagamento', S_table_cell),
         Paragraph('payment', S_table_cell)],
        [Paragraph('3 Rate', S_table_cell),
         Paragraph('€390 (€130 × 3)', S_table_cell),
         Paragraph('3 rate mensili', S_table_cell),
         Paragraph('subscription', S_table_cell)],
    ]
    ut = Table(urban_data, colWidths=[50*mm, 35*mm, 45*mm, 30*mm])
    ut.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NERO),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [BIANCO, GRIGIO_L]),
        ('GRID', (0,0), (-1,-1), 0.5, GRIGIO_M),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(ut)
    story.append(Spacer(1, 5*mm))

    # Motion
    story.append(Paragraph('Lume Motion', S_h2))
    motion_data = [
        [Paragraph('<b>Piano</b>', S_table_head),
         Paragraph('<b>Prezzo</b>', S_table_head),
         Paragraph('<b>Modalità</b>', S_table_head),
         Paragraph('<b>Stripe mode</b>', S_table_head)],
        [Paragraph('Motion — Soluzione Unica', S_table_cell),
         Paragraph('€480', S_table_cell),
         Paragraph('1 pagamento', S_table_cell),
         Paragraph('payment', S_table_cell)],
        [Paragraph('Motion — 4 Rate', S_table_cell),
         Paragraph('€520 (€130 × 4)', S_table_cell),
         Paragraph('4 rate mensili', S_table_cell),
         Paragraph('subscription', S_table_cell)],
        [Paragraph('Motion BOX — Soluzione Unica', S_table_cell),
         Paragraph('€720', S_table_cell),
         Paragraph('1 pagamento', S_table_cell),
         Paragraph('payment', S_table_cell)],
        [Paragraph('Motion BOX — 6 Rate', S_table_cell),
         Paragraph('€780 (€130 × 6)', S_table_cell),
         Paragraph('6 rate mensili', S_table_cell),
         Paragraph('subscription', S_table_cell)],
    ]
    mt = Table(motion_data, colWidths=[55*mm, 32*mm, 40*mm, 33*mm])
    mt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NERO),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [BIANCO, GRIGIO_L]),
        ('GRID', (0,0), (-1,-1), 0.5, GRIGIO_M),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(mt)
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(
        'Le rate Stripe sono subscription mensili da €130. n8n ascolta l\'evento '
        '<b>invoice.paid</b> e cancella automaticamente la subscription dopo N pagamenti '
        '(valore in metadata: <i>installments_total</i>).',
        S_body))
    story.append(PageBreak())

    # ── 5. Webhooks ──────────────────────────────────────────────────────────
    story.append(Paragraph('5. Integrazione Webhooks n8n', S_section))
    story.append(hr())

    wh_data = [
        ['verifica-iscritto',
         'n8n.lumeflow.it/webhook/\nverifica-iscritto',
         'Invio dati personali',
         'Controlla se già cliente;\nritorna proceed:true/false'],
        ['FIRMA-CONTRATTO',
         'n8n.lumeflow.it/webhook/\nFIRMA-CONTRATTO',
         'Firma apposta',
         'Salva contratto HTML + firma_base64 su Airtable; status → "Contratto firmato"'],
        ['conferma-stripe',
         'n8n.lumeflow.it/webhook/\nconferma-stripe',
         'Redirect ?payment=\nsuccess da Stripe',
         'Aggiorna Airtable; genera PDF Gotenberg; invia email SendGrid'],
    ]
    story.append(webhook_table(wh_data))
    story.append(Spacer(1, 5*mm))

    story.append(Paragraph('Payload webhook FIRMA-CONTRATTO (campi principali)', S_h3))
    payload_code = (
        'email, nome, cognome, codice_fiscale\n'
        'piano_id, piano_nome, importo, rate\n'
        'sede\n'
        'firma_base64     ← PNG firma (puro base64, senza prefisso data:)\n'
        'contratto_html   ← HTML completo del contratto firmato'
    )
    story.append(Paragraph(payload_code, S_code))
    story.append(Spacer(1, 4*mm))

    story.append(Paragraph('Payload webhook conferma-stripe (ricostruito da sessionStorage)', S_h3))
    payload2_code = (
        'email, nome, cognome, codice_fiscale\n'
        'piano_id, piano_nome, importo, rate\n'
        'sede\n'
        'firma_base64     ← recuperato da sessionStorage\n'
        'stripe_session_id\n'
        '[nota: contratto_html escluso per evitare QuotaExceededError su sessionStorage]'
    )
    story.append(Paragraph(payload2_code, S_code))
    story.append(PageBreak())

    # ── 6. Stripe ────────────────────────────────────────────────────────────
    story.append(Paragraph('6. Integrazione Stripe', S_section))
    story.append(hr())
    story.append(Paragraph(
        'Il pagamento avviene tramite <b>Stripe Checkout</b> (pagina hosted Stripe). '
        'La secret key è gestita lato server da una Netlify Function '
        '(<i>api/create-checkout.js</i>) per non esporla mai al browser.',
        S_body))
    story.append(Spacer(1, 4*mm))

    stripe_data = [
        [Paragraph('<b>Tipo</b>', S_table_head),
         Paragraph('<b>Stripe mode</b>', S_table_head),
         Paragraph('<b>Dettaglio</b>', S_table_head)],
        [Paragraph('Pagamento unico', S_table_cell),
         Paragraph('mode: payment', S_table_cell),
         Paragraph('Importo fisso in centesimi, PaymentIntent', S_table_cell)],
        [Paragraph('Rateizzato', S_table_cell),
         Paragraph('mode: subscription', S_table_cell),
         Paragraph('€130/mese; n8n cancella dopo N rate (metadata: installments_total)', S_table_cell)],
    ]
    st = Table(stripe_data, colWidths=[38*mm, 40*mm, 82*mm])
    st.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NERO),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [BIANCO, GRIGIO_L]),
        ('GRID', (0,0), (-1,-1), 0.5, GRIGIO_M),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(st)
    story.append(Spacer(1, 5*mm))

    story.append(Paragraph('Variabili d\'ambiente richieste (Netlify)', S_h3))
    env_data = [
        [Paragraph('<b>Variabile</b>', S_table_head), Paragraph('<b>Descrizione</b>', S_table_head)],
        [Paragraph('STRIPE_SECRET_KEY', S_table_cell), Paragraph('Secret key Stripe (sk_live_...)', S_table_cell)],
        [Paragraph('ALLOWED_ORIGIN', S_table_cell), Paragraph('Opzionale — dominio consentito CORS (default *)', S_table_cell)],
    ]
    et = Table(env_data, colWidths=[55*mm, 105*mm])
    et.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NERO),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [BIANCO, GRIGIO_L]),
        ('GRID', (0,0), (-1,-1), 0.5, GRIGIO_M),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(et)
    story.append(PageBreak())

    # ── 7. Contratto digitale ────────────────────────────────────────────────
    story.append(Paragraph('7. Contratto Digitale', S_section))
    story.append(hr())
    story.append(Paragraph(
        'Prima del pagamento, il sistema genera al volo un contratto HTML '
        'personalizzato con i dati dell\'iscritto. L\'utente appone la propria '
        'firma digitale tramite Canvas API, che viene catturata come PNG in base64.',
        S_body))
    story.append(Spacer(1, 4*mm))

    story.append(Paragraph('Contenuto del contratto', S_h3))
    contract_items = [
        '•  Dati anagrafici iscritto (e genitore se minorenne)',
        '•  Sede, piano scelto, importo totale',
        '•  Scadenza: 12 mesi dall\'apertura ufficiale della sede',
        '•  Calendario rate (se rateizzato)',
        '•  Consensi obbligatori accettati (termini e condizioni, clausole vessatorie)',
        '•  Firma digitale embedded come immagine PNG',
        '•  Data e ora della firma',
    ]
    for item in contract_items:
        story.append(Paragraph(item, S_bullet))
    story.append(Spacer(1, 4*mm))

    story.append(Paragraph('Ciclo di vita del contratto', S_h3))
    contract_life = [
        ('1', 'Generazione HTML', 'JavaScript genera il contratto con i dati del form al momento della firma'),
        ('2', 'Firma Canvas', 'L\'utente firma nel riquadro apposito; il PNG viene catturato (data URL)'),
        ('3', 'Webhook FIRMA-CONTRATTO', 'HTML + firma_base64 inviati a n8n e salvati su Airtable'),
        ('4', 'Post-pagamento', 'n8n converte l\'HTML in PDF tramite Gotenberg (gotenberg.lumeflow.it)'),
        ('5', 'Archiviazione Cloudinary', 'PDF caricato su Cloudinary (Resource Type: Raw) per ottenere un URL pubblico permanente; URL salvato nel record Airtable come allegato'),
        ('6', 'Invio email', 'SendGrid invia il contratto PDF all\'indirizzo dell\'iscritto tramite il link Cloudinary'),
    ]
    story.append(step_table(contract_life))
    story.append(PageBreak())

    # ── 8. Airtable ──────────────────────────────────────────────────────────
    story.append(Paragraph('8. Airtable — CRM, Tracking e Interfaccia di Controllo', S_section))
    story.append(hr())
    story.append(Paragraph(
        'Ogni pre-iscrizione viene tracciata in Airtable con uno status che '
        'evolve lungo il flow. La segreteria può aggiornare manualmente i record '
        'per i pagamenti in sede (contanti, bonifico, POS). '
        'E\' disponibile un\'<b>interfaccia di controllo personalizzata su Airtable</b> '
        'che permette al team di monitorare in tempo reale lo stato di ogni lead per sede.',
        S_body))
    story.append(Spacer(1, 4*mm))

    story.append(Paragraph('Stati del record', S_h3))
    status_data = [
        [Paragraph('<b>Status</b>', S_table_head),
         Paragraph('<b>Trigger</b>', S_table_head),
         Paragraph('<b>Azione automatica</b>', S_table_head)],
        [Paragraph('In attesa', S_table_cell),
         Paragraph('Webhook verifica-iscritto (proceed:true)', S_table_cell),
         Paragraph('—', S_table_cell)],
        [Paragraph('Contratto firmato', S_table_cell),
         Paragraph('Webhook FIRMA-CONTRATTO', S_table_cell),
         Paragraph('Salva contratto HTML + firma', S_table_cell)],
        [Paragraph('Pagamento completato', S_table_cell),
         Paragraph('Webhook conferma-stripe', S_table_cell),
         Paragraph('Genera PDF, invia email contratto', S_table_cell)],
        [Paragraph('Pagato (sede)', S_table_cell),
         Paragraph('Segreteria — aggiornamento manuale', S_table_cell),
         Paragraph('Sistema invia automaticamente il contratto via email', S_table_cell)],
    ]
    airt = Table(status_data, colWidths=[38*mm, 60*mm, 62*mm])
    airt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NERO),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [BIANCO, GRIGIO_L]),
        ('GRID', (0,0), (-1,-1), 0.5, GRIGIO_M),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(airt)
    story.append(Spacer(1, 5*mm))

    story.append(Paragraph('Campi principali nel record Airtable', S_h3))
    fields_cols = [
        ['Nome', 'Cognome', 'Email', 'Telefono', 'Codice Fiscale',
         'Data di Nascita', 'Comune', 'Sede', 'Piano', 'Importo', 'Rate'],
        ['Status', 'Metodo pagamento', 'Stripe Session ID',
         'Contratto HTML', 'Firma base64', 'PDF contratto (URL Cloudinary)',
         'Data firma', 'Note segreteria', 'UTM Source', 'UTM Medium', 'UTM Campaign',
         'Genitore Nome', 'Genitore Cognome', 'Genitore CF'],
    ]
    for col in fields_cols:
        for f in col:
            story.append(Paragraph(f'•  {f}', S_bullet))
    story.append(Spacer(1, 4*mm))

    story.append(Paragraph('Tracciamento UTM', S_h3))
    story.append(Paragraph(
        'I parametri UTM vengono catturati automaticamente dall\'URL di atterraggio '
        'e salvati in sessionStorage, in modo da sopravvivere al redirect verso Stripe '
        'e al ritorno sulla pagina. Vengono propagati in tutti e 3 i webhook '
        '(verifica-iscritto, FIRMA-CONTRATTO, conferma-stripe) e salvati su Airtable.',
        S_body))
    story.append(Spacer(1, 4*mm))

    utm_data = [
        [Paragraph('<b>Parametro URL</b>', S_table_head),
         Paragraph('<b>Campo Airtable</b>', S_table_head),
         Paragraph('<b>Descrizione</b>', S_table_head),
         Paragraph('<b>Esempi di valore</b>', S_table_head)],
        [Paragraph('utm_source', S_code),
         Paragraph('UTM Source', S_table_cell),
         Paragraph('Sorgente del traffico', S_table_cell),
         Paragraph('facebook, instagram, google, newsletter', S_table_cell)],
        [Paragraph('utm_medium', S_code),
         Paragraph('UTM Medium', S_table_cell),
         Paragraph('Canale/tipo di media', S_table_cell),
         Paragraph('cpc, paid_social, email, organic', S_table_cell)],
        [Paragraph('utm_campaign', S_code),
         Paragraph('UTM Campaign', S_table_cell),
         Paragraph('Nome della campagna', S_table_cell),
         Paragraph('urban_earlybird, motion_lancio, promo_estate', S_table_cell)],
        [Paragraph('utm_content', S_code),
         Paragraph('UTM Content', S_table_cell),
         Paragraph('Variante creativa/annuncio', S_table_cell),
         Paragraph('video_a, banner_b, stories_1', S_table_cell)],
        [Paragraph('utm_term', S_code),
         Paragraph('UTM Term', S_table_cell),
         Paragraph('Keyword (Google Ads)', S_table_cell),
         Paragraph('palestra macerata, abbonamento fitness', S_table_cell)],
    ]
    utm_t = Table(utm_data, colWidths=[32*mm, 30*mm, 42*mm, 56*mm])
    utm_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NERO),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [BIANCO, GRIGIO_L]),
        ('GRID', (0,0), (-1,-1), 0.5, GRIGIO_M),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(utm_t)
    story.append(Spacer(1, 4*mm))

    story.append(Paragraph('Esempio URL con UTM', S_h3))
    utm_url = (
        'https://promo.lumefitness.it/urban.html\n'
        '  ?utm_source=facebook\n'
        '  &utm_medium=paid_social\n'
        '  &utm_campaign=urban_earlybird\n'
        '  &utm_content=video_a'
    )
    story.append(Paragraph(utm_url, S_code))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        '<b>Nota:</b> se l\'URL non contiene parametri UTM, i campi restano vuoti '
        'nel record Airtable — nessun errore viene generato.',
        S_body))
    story.append(PageBreak())

    # ── 9. Pagamento in sede ─────────────────────────────────────────────────
    story.append(Paragraph('9. Pagamento in Sede — Canale Dedicato', S_section))
    story.append(hr())
    story.append(Paragraph(
        'La segreteria può condividere un link speciale con il parametro '
        '<b>?canale=sede</b> per abilitare metodi di pagamento alternativi a Stripe '
        'direttamente nel form online. Il cliente completa autonomamente il form '
        'e firma il contratto digitale, scegliendo come pagare.',
        S_body))
    story.append(Spacer(1, 4*mm))

    story.append(Paragraph('URL dedicato alla segreteria', S_h3))
    story.append(Paragraph(
        'https://promo.lumefitness.it/urban.html?canale=sede\n'
        'https://promo.lumefitness.it/motion.html?canale=sede',
        S_code))
    story.append(Spacer(1, 4*mm))

    story.append(Paragraph('Metodi di pagamento disponibili', S_h3))
    metodi_data = [
        [Paragraph('<b>Metodo</b>', S_table_head),
         Paragraph('<b>Valore nel webhook</b>', S_table_head),
         Paragraph('<b>Messaggio Step 5</b>', S_table_head)],
        [Paragraph('Carta (Stripe)', S_table_cell),
         Paragraph('stripe', S_code),
         Paragraph('Flow Stripe normale — redirect e conferma', S_table_cell)],
        [Paragraph('Contanti in sede', S_table_cell),
         Paragraph('contanti', S_code),
         Paragraph('"Presentati in sede e paga in contanti alla reception"', S_table_cell)],
        [Paragraph('POS in sede', S_table_cell),
         Paragraph('pos', S_code),
         Paragraph('"Presentati in sede e paga con il POS alla reception"', S_table_cell)],
        [Paragraph('Bonifico bancario', S_table_cell),
         Paragraph('bonifico', S_code),
         Paragraph('"Riceverai via email le coordinate bancarie"', S_table_cell)],
    ]
    mt = Table(metodi_data, colWidths=[35*mm, 28*mm, 97*mm])
    mt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NERO),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [BIANCO, GRIGIO_L]),
        ('GRID', (0,0), (-1,-1), 0.5, GRIGIO_M),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(mt)
    story.append(Spacer(1, 4*mm))

    story.append(Paragraph('Logica di funzionamento', S_h3))
    story.append(Paragraph(
        '<b>Il selettore appare solo per piani a soluzione unica</b> (rate === 1). '
        'I piani rateizzati vanno sempre su Stripe, indipendentemente dal parametro canale.',
        S_body))
    story.append(Spacer(1, 3*mm))

    in_sede = [
        ('1', 'Iscritto apre il link ?canale=sede', 'La pagina rileva il parametro all\'avvio'),
        ('2', 'Sceglie piano unico', 'Appare il selettore metodo pagamento nello step contratto'),
        ('3', 'Firma il contratto', 'Webhook FIRMA-CONTRATTO inviato con metodo_pagamento nel payload'),
        ('4', 'Sceglie metodo alternativo', 'Webhook conferma-stripe inviato con metodo_pagamento e canale: "sede"'),
        ('5', 'Step 5 — conferma', 'Messaggio specifico per il metodo scelto (contanti / POS / bonifico)'),
        ('6', 'n8n su Airtable', 'Status → "In attesa pagamento sede", Metodo pagamento salvato'),
        ('7', 'Pagamento ricevuto', 'Segreteria aggiorna Status → "Pagato"; n8n invia contratto PDF via email'),
    ]
    story.append(step_table(in_sede))
    story.append(Spacer(1, 4*mm))

    story.append(Paragraph(
        '<b>Nota:</b> il contratto HTML + firma_base64 sono già inviati '
        'al webhook FIRMA-CONTRATTO prima della scelta del metodo, quindi n8n dispone '
        'di tutti i dati per generare il PDF indipendentemente da come avviene il pagamento.',
        S_body))
    story.append(PageBreak())

    # ── 10. Deploy e infrastruttura ──────────────────────────────────────────
    story.append(Paragraph('10. Deploy e Infrastruttura', S_section))
    story.append(hr())
    story.append(Paragraph(
        'Il sistema e\' <b>live in produzione</b> su <b>promo.lumefitness.it</b>. '
        'Tutte le pagine sono ottimizzate per la SEO con meta tag description, '
        'Open Graph (Facebook/Instagram), Twitter Card e URL canonical '
        'puntati al sottodominio promo.lumefitness.it.',
        S_body))
    story.append(Spacer(1, 4*mm))

    deploy_data = [
        [Paragraph('<b>Componente</b>', S_table_head),
         Paragraph('<b>Dettaglio</b>', S_table_head)],
        [Paragraph('Repository', S_table_cell),
         Paragraph('GitHub — branch main', S_table_cell)],
        [Paragraph('Hosting', S_table_cell),
         Paragraph('Netlify (deploy automatico da main)', S_table_cell)],
        [Paragraph('Dominio', S_table_cell),
         Paragraph('promo.lumefitness.it — LIVE (CNAME verso Netlify)', S_table_cell)],
        [Paragraph('Funzioni serverless', S_table_cell),
         Paragraph('api/create-checkout.js → /.netlify/functions/create-checkout', S_table_cell)],
        [Paragraph('Env vars Netlify', S_table_cell),
         Paragraph('STRIPE_SECRET_KEY (obbligatorio)', S_table_cell)],
        [Paragraph('n8n', S_table_cell),
         Paragraph('Self-hosted su n8n.lumeflow.it', S_table_cell)],
        [Paragraph('Gotenberg', S_table_cell),
         Paragraph('Self-hosted su gotenberg.lumeflow.it', S_table_cell)],
        [Paragraph('Cloudinary', S_table_cell),
         Paragraph('Archiviazione PDF contratti (Resource Type: Raw per visualizzazione diretta)', S_table_cell)],
        [Paragraph('SEO', S_table_cell),
         Paragraph('Meta description, Open Graph, Twitter Card, canonical su tutte le pagine', S_table_cell)],
    ]
    dt = Table(deploy_data, colWidths=[50*mm, 110*mm])
    dt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NERO),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [BIANCO, GRIGIO_L]),
        ('GRID', (0,0), (-1,-1), 0.5, GRIGIO_M),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(dt)
    story.append(Spacer(1, 5*mm))

    story.append(Paragraph('File del progetto', S_h3))
    files_data = [
        [Paragraph('<b>File</b>', S_table_head), Paragraph('<b>Descrizione</b>', S_table_head)],
        [Paragraph('index.html', S_table_cell), Paragraph('Landing page con selezione sede', S_table_cell)],
        [Paragraph('promo.html', S_table_cell), Paragraph('Form Guest Pass 7gg (HQ + Balance)', S_table_cell)],
        [Paragraph('urban.html', S_table_cell), Paragraph('Form prevendita Lume Urban', S_table_cell)],
        [Paragraph('motion.html', S_table_cell), Paragraph('Form prevendita Lume Motion', S_table_cell)],
        [Paragraph('api/create-checkout.js', S_table_cell), Paragraph('Netlify Function — crea Stripe Checkout Session', S_table_cell)],
        [Paragraph('netlify.toml', S_table_cell), Paragraph('Configurazione build e redirect Netlify', S_table_cell)],
    ]
    ft = Table(files_data, colWidths=[55*mm, 105*mm])
    ft.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NERO),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [BIANCO, GRIGIO_L]),
        ('GRID', (0,0), (-1,-1), 0.5, GRIGIO_M),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(ft)
    story.append(PageBreak())

    # ── 11. Roadmap ──────────────────────────────────────────────────────────
    story.append(Paragraph('11. Sviluppi Futuri', S_section))
    story.append(hr())
    story.append(Paragraph(
        'Il sistema e\' operativo e in produzione. I prossimi sviluppi pianificati '
        'riguardano l\'integrazione con il gestionale PerfectGym (PGM) e '
        'l\'evoluzione delle pagine di prevendita in pagine promozionali a regime.',
        S_body))
    story.append(Spacer(1, 5*mm))

    roadmap_items = [
        ('Invio contratti a PerfectGym',
         'Al completamento del pagamento (o alla conferma in sede), n8n invia automaticamente '
         'il contratto firmato a PerfectGym tramite API, creando il profilo iscritto '
         'e allegando il documento direttamente nel gestionale.'),
        ('Invio transazioni rateali a PerfectGym',
         'Ogni evento invoice.paid di Stripe viene propagato a PerfectGym per mantenere '
         'lo storico pagamenti allineato. n8n intercetta l\'evento, verifica il numero di '
         'rata (metadata: installments_paid vs installments_total) e aggiorna la posizione '
         'finanziaria dell\'iscritto nel gestionale.'),
        ('Transizione da Prevendita a PROMO — Lume Urban e Lume Motion',
         'All\'apertura ufficiale delle due nuove sedi, le pagine urban.html e motion.html '
         'verranno convertite da flow di prevendita Early Bird a pagine promozionali standard, '
         'analoghe al Guest Pass di HQ e Balance. Il sistema rimane invariato; '
         'cambia solo la logica di pricing e l\'offerta presentata all\'utente.'),
    ]

    for i, (title, desc) in enumerate(roadmap_items, 1):
        rd = [[
            Paragraph(str(i), style('Normal', fontSize=16, textColor=GIALLO,
                                     fontName='Helvetica-Bold', alignment=TA_CENTER)),
            [Paragraph(f'<b>{title}</b>', S_h3),
             Spacer(1, 2*mm),
             Paragraph(desc, S_body)]
        ]]
        rt = Table(rd, colWidths=[16*mm, 144*mm])
        rt.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('BACKGROUND', (0,0), (0,-1), NERO),
            ('BACKGROUND', (1,0), (1,-1), GRIGIO_L),
            ('LEFTPADDING', (1,0), (1,-1), 10),
            ('LINEBELOW', (0,0), (-1,-1), 0.5, GRIGIO_M),
        ]))
        story.append(rt)
        story.append(Spacer(1, 3*mm))
    story.append(PageBreak())

    # ── 12. Riepilogo URL ────────────────────────────────────────────────────
    story.append(Paragraph('12. Riepilogo URL e Endpoint', S_section))
    story.append(hr())

    url_data = [
        [Paragraph('<b>Descrizione</b>', S_table_head), Paragraph('<b>URL</b>', S_table_head)],
        [Paragraph('Landing page', S_table_cell), Paragraph('https://promo.lumefitness.it', S_table_cell)],
        [Paragraph('Guest Pass (HQ/Balance)', S_table_cell), Paragraph('https://promo.lumefitness.it/promo.html', S_table_cell)],
        [Paragraph('Prevendita Lume Urban', S_table_cell), Paragraph('https://promo.lumefitness.it/urban.html', S_table_cell)],
        [Paragraph('Prevendita Lume Motion', S_table_cell), Paragraph('https://promo.lumefitness.it/motion.html', S_table_cell)],
        [Paragraph('API Stripe Checkout', S_table_cell), Paragraph('https://promo.lumefitness.it/api/create-checkout', S_table_cell)],
        [Paragraph('Webhook verifica-iscritto', S_table_cell), Paragraph('https://n8n.lumeflow.it/webhook/verifica-iscritto', S_table_cell)],
        [Paragraph('Webhook FIRMA-CONTRATTO', S_table_cell), Paragraph('https://n8n.lumeflow.it/webhook/FIRMA-CONTRATTO', S_table_cell)],
        [Paragraph('Webhook conferma-stripe', S_table_cell), Paragraph('https://n8n.lumeflow.it/webhook/conferma-stripe', S_table_cell)],
        [Paragraph('Gotenberg PDF', S_table_cell), Paragraph('https://gotenberg.lumeflow.it', S_table_cell)],
    ]
    url_t = Table(url_data, colWidths=[55*mm, 105*mm])
    url_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NERO),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [BIANCO, GRIGIO_L]),
        ('GRID', (0,0), (-1,-1), 0.5, GRIGIO_M),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('FONTNAME', (1,1), (1,-1), 'Courier'),
        ('FONTSIZE', (1,1), (1,-1), 8),
    ]))
    story.append(url_t)

    return story


# ── Footer ───────────────────────────────────────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    # Footer bar
    canvas.setFillColor(NERO)
    canvas.rect(0, 0, W, 18*mm, fill=1, stroke=0)
    canvas.setFillColor(GIALLO)
    canvas.setFont('Helvetica-Bold', 8)
    canvas.drawString(20*mm, 8*mm, 'LUME FITNESS')
    canvas.setFillColor(GRIGIO_M)
    canvas.setFont('Helvetica', 7)
    canvas.drawString(20*mm, 4*mm, 'Documentazione Sistema Prevendita — promo.lumefitness.it')
    # Page number
    canvas.setFillColor(BIANCO)
    canvas.setFont('Helvetica', 8)
    canvas.drawRightString(W - 20*mm, 6*mm, f'Pag. {doc.page}')
    canvas.restoreState()


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    output_path = '/Users/mauriziotaruggi/Documents/GitHub/lume-prevendita/Lume_Fitness_Prevendita_Flow.pdf'
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=20*mm,
        rightMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=22*mm,
        title='Lume Fitness — Sistema Prevendita & Promozioni',
        author='Lume Fitness',
        subject='Documentazione tecnica e di processo — Giugno 2026',
    )
    story = build_story()
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f'PDF generato: {output_path}')
