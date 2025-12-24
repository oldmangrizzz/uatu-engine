#!/usr/bin/env python3
"""Generate a 4-slide counsel brief PDF for the Uatu Genesis Engine.
Produces REVIEW_NOTES/COUNSEL_SLIDES.pdf and REVIEW_NOTES/COUNSEL_SLIDES_NOTES.md
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from textwrap import wrap

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas

OUT_PDF = Path("REVIEW_NOTES/COUNSEL_SLIDES.pdf")
OUT_NOTES = Path("REVIEW_NOTES/COUNSEL_SLIDES_NOTES.md")
COMMIT = "4851251c3d158e56beacf077d4b49e50bd630388"

PAGE_WIDTH, PAGE_HEIGHT = letter
MARGIN = 0.75 * inch


def draw_title_slide(c: Canvas):
    title = "Uatu Genesis Engine — Counsel Brief"
    subtitle = f"Commit: {COMMIT}    •    {datetime.utcnow().date().isoformat()}"
    bullets = [
        "Emergence Gate: single-admin ECDSA P-256 gate, passphrase-encrypted private key, signed triggers, admin overrides",
        "Digital Psyche Middleware (DPM): reproducible emergent persona behavior via LLM modifiers and update cycles",
        "Auditable logging: append-only events.jsonl + Convex local backups for provenance and forensics",
    ]

    c.setFont("Helvetica-Bold", 28)
    c.drawString(MARGIN, PAGE_HEIGHT - MARGIN - 40, title)
    c.setFont("Helvetica", 10)
    c.drawString(MARGIN, PAGE_HEIGHT - MARGIN - 60, subtitle)

    y = PAGE_HEIGHT - MARGIN - 120
    c.setFont("Helvetica", 12)
    for b in bullets:
        lines = wrap(b, 85)
        c.drawString(MARGIN + 12, y, "• " + lines[0])
        y -= 16
        for ln in lines[1:]:
            c.drawString(MARGIN + 28, y, ln)
            y -= 14
        y -= 8


def draw_claims_slide(c: Canvas):
    title = "Key Claims & Invention Areas"
    bullets = [
        ("DPM (Digital Psyche Middleware)",
         "Middleware enabling reproducible emergent behavior through layered LLM modifiers and a neurotransmitter-inspired update cycle. Claim families: system, method, signal flow."),
        ("Emergence Gate", "Cryptographic gate controlling identity permission surfaces (signed triggers, admin overrides) with auditable transition logging."),
        ("Auditable Provenance", "Convex-state logger + local append-only backups enabling forensic reconstruction and tamper-evident attestation."),
    ]

    c.setFont("Helvetica-Bold", 20)
    c.drawString(MARGIN, PAGE_HEIGHT - MARGIN - 40, title)
    y = PAGE_HEIGHT - MARGIN - 80
    c.setFont("Helvetica-Bold", 12)
    for h, text in bullets:
        c.drawString(MARGIN + 6, y, "• " + h)
        y -= 16
        c.setFont("Helvetica", 11)
        for ln in wrap(text, 100):
            c.drawString(MARGIN + 28, y, ln)
            y -= 14
        y -= 10
        c.setFont("Helvetica-Bold", 12)


def draw_gtp_slide(c: Canvas):
    title = "Communication Protocol — Grizzly Translation Protocol (GTP)"
    bullets = [
        ("Purpose & Scope",
         "Temporary voice/reasoning overlay for high-density, accountable communication. Does NOT transfer identity or attribute authorship."),
        ("Activation & Triggers",
         "Explicit-only activation (e.g., 'write this in my voice', 'translate into my voice'); ambiguity defaults to non-GTP."),
        ("Core Principles",
         "Assume competence; intent over surface; no infantilization; burden-sharing; system owns generated language."),
        ("Pseudocode Policy",
         "Pseudocode treated as disallowed — outputs must be implementable or labeled speculative.")
    ]

    c.setFont("Helvetica-Bold", 18)
    c.drawString(MARGIN, PAGE_HEIGHT - MARGIN - 40, title)
    y = PAGE_HEIGHT - MARGIN - 80
    c.setFont("Helvetica-Bold", 12)
    for h, text in bullets:
        c.drawString(MARGIN + 6, y, "• " + h)
        y -= 14
        c.setFont("Helvetica", 11)
        for ln in wrap(text, 100):
            c.drawString(MARGIN + 28, y, ln)
            y -= 14
        y -= 8
        c.setFont("Helvetica-Bold", 12)


def draw_evidence_slide(c: Canvas):
    title = "Evidence & Counsel Action Items"
    bullets = [
        ("Evidence to Archive",
         "DPM experiment seeds + transcripts; events.jsonl (state transitions, edit_rejection/edit_override); Convex local backups; persona_config snapshots; encrypted private package."),
        ("Immediate Asks for Counsel",
         "Review claim language; advise on priority claims; confirm retention and chain-of-custody; recommend jurisdictional considerations and OOB passphrase transfer method."),
        ("Operational Recommendations",
         "Encrypted private keys; documented OOB passphrase sharing; annual key rotation; dual-sign for wildcard overrides; regular audit cadence."),
    ]

    c.setFont("Helvetica-Bold", 20)
    c.drawString(MARGIN, PAGE_HEIGHT - MARGIN - 40, title)
    y = PAGE_HEIGHT - MARGIN - 80
    c.setFont("Helvetica-Bold", 12)
    for h, text in bullets:
        c.drawString(MARGIN + 6, y, "• " + h)
        y -= 16
        c.setFont("Helvetica", 11)
        for ln in wrap(text, 100):
            c.drawString(MARGIN + 28, y, ln)
            y -= 14
        y -= 10
        c.setFont("Helvetica-Bold", 12)


def draw_contact_slide(c: Canvas):
    title = "Contacts & Next Steps"
    c.setFont("Helvetica-Bold", 20)
    c.drawString(MARGIN, PAGE_HEIGHT - MARGIN - 40, title)

    lines = [
        "Next steps for counsel:",
        "- Review claim language and advise on priority claims for provisional filing.",
        "- Confirm secure OOB channel for passphrase transfer and chain-of-custody.",
        "- Recommend retention period and jurisdictions for storage/compliance.",
        "",
        f"Commit: {COMMIT}",
        "Files to share for review (encrypted): REVIEW_NOTES/PRIVATE_FULL_PROVISIONAL_ENCRYPTED_20251224.bin",
    ]

    y = PAGE_HEIGHT - MARGIN - 80
    c.setFont("Helvetica", 12)
    for ln in lines:
        for wrap_ln in wrap(ln, 100):
            c.drawString(MARGIN + 6, y, wrap_ln)
            y -= 14
        y -= 6


def generate_pdf():
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    c = Canvas(str(OUT_PDF), pagesize=letter)

    draw_title_slide(c)
    c.showPage()

    draw_claims_slide(c)
    c.showPage()

    draw_evidence_slide(c)
    c.showPage()

    draw_contact_slide(c)
    c.showPage()

    c.save()

    # speaker notes
    notes = f"""Slide 1 — Executive Summary
- One-line summary of the system and current commit: {COMMIT}

Slide 2 — Key Claims & Invention Areas
- Explain DPM as middleware; include method/system claims and example experimental evidence
- Discuss Emergence Gate: cryptographic gating, signed triggers, audit trail

Slide 3 — Evidence & Counsel Action Items
- Point to specific evidence sets (events.jsonl, Convex backups, seed experiments)
- Ask counsel to prioritize claims and advise on retention

Slide 4 — Contacts & Next Steps
- Confirm secure OOB passphrase channel, mention file name of encrypted package
"""
    OUT_NOTES.write_text(notes, encoding="utf-8")
    return OUT_PDF, OUT_NOTES


if __name__ == "__main__":
    pdf, notes = generate_pdf()
    print(f"Generated: {pdf} ({pdf.stat().st_size} bytes)")
    print(f"Speaker notes: {notes}")
