#!/usr/bin/env python3
"""Generate a one-page counsel handout PDF for quick reference.
Produces REVIEW_NOTES/COUNSEL_HANDOUT.pdf and REVIEW_NOTES/COUNSEL_HANDOUT.md
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from textwrap import wrap

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas

OUT_PDF = Path("REVIEW_NOTES/COUNSEL_HANDOUT.pdf")
OUT_MD = Path("REVIEW_NOTES/COUNSEL_HANDOUT.md")
COMMIT = "4851251c3d158e56beacf077d4b49e50bd630388"

PAGE_WIDTH, PAGE_HEIGHT = letter
MARGIN = 0.75 * inch


def generate_pdf():
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    c = Canvas(str(OUT_PDF), pagesize=letter)

    title = "Uatu Genesis Engine — Counsel Handout"
    subtitle = f"Commit: {COMMIT}    •    {datetime.utcnow().date().isoformat()}"

    c.setFont("Helvetica-Bold", 18)
    c.drawString(MARGIN, PAGE_HEIGHT - MARGIN - 40, title)
    c.setFont("Helvetica", 9)
    c.drawString(MARGIN, PAGE_HEIGHT - MARGIN - 60, subtitle)

    y = PAGE_HEIGHT - MARGIN - 100
    sections = [
        ("Core Components", [
            "Emergence Gate: single-admin ECDSA P-256 key, passphrase-encrypted, signed triggers, admin overrides.",
            "Digital Psyche Middleware (DPM): reproducible emergent persona behavior via layered LLM modifiers.",
            "Auditable Provenance: local append-only events.jsonl + Convex local backups for forensics.",
        ]),
        ("Immediate Counsel Items", [
            "Review provisional claims: DPM method/system/flow; Emergence Gate signed gating + auditable logging.",
            "Confirm retention and chain-of-custody for encrypted package; advise on jurisdictional implications.",
        ]),
        ("Operational Recommendations", [
            "Keep private keys encrypted; use HSM if possible; documented OOB passphrase transfer; log disclosures.",
            "Require time-limited overrides and dual-sign for wildcard overrides; maintain weekly audit cadence.",
        ]),
    ]

    c.setFont("Helvetica-Bold", 12)
    for header, lines in sections:
        c.drawString(MARGIN, y, header)
        y -= 16
        c.setFont("Helvetica", 10)
        for l in lines:
            for ln in wrap(l, 90):
                c.drawString(MARGIN + 10, y, "- " + ln)
                y -= 12
        y -= 8
        c.setFont("Helvetica-Bold", 12)

    c.save()
    return OUT_PDF


def generate_md():
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    md = f"""# Counsel Handout — Uatu Genesis Engine

Commit: {COMMIT}

## Core Components
- Emergence Gate: single-admin ECDSA P-256 key, passphrase-encrypted, signed triggers, admin overrides.
- Digital Psyche Middleware (DPM): reproducible emergent persona behavior via layered LLM modifiers.
- Auditable Provenance: local append-only events.jsonl + Convex local backups for forensics.

## Immediate Counsel Items
- Review provisional claims: DPM method/system/flow; Emergence Gate signed gating + auditable logging.
- Confirm retention and chain-of-custody for encrypted package; advise on jurisdictional implications.

## Operational Recommendations
- Keep private keys encrypted; use HSM if possible; documented OOB passphrase transfer; log disclosures.
- Require time-limited overrides and dual-sign for wildcard overrides; maintain weekly audit cadence.
"""
    OUT_MD.write_text(md, encoding="utf-8")
    return OUT_MD


if __name__ == "__main__":
    pdf = generate_pdf()
    md = generate_md()
    print(f"Generated: {pdf} ({pdf.stat().st_size} bytes)")
    print(f"Notes: {md}")
