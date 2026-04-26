# business_sober_v1 — Style Guide

**Kit ID:** `business_sober_v1` · **Package:** `entrepreneur_v1` · **Schema:** v1.1.0
**Reference style:** McKinsey 2-pager, KKR board pack, Bain situation-complication-resolution.

## When to use

This kit ships everything an SME founder, CFO or board chair needs to brief
a Verwaltungsrat in ten minutes and price the policy shock in CHF: a 2-page
risk memo with three risks and three levers, an XLSX cost calculator the
treasurer can re-run with new exposure assumptions, a single board PPTX
slide that condenses the memo onto one canvas, and a corporate email that
links to the PDF without leaking sensitive figures into preview panes. The
register is sober: no McKinsey-deck colour theatre, no consulting jargon
ladder, just a navy-grey palette with a single gold accent on the
recommendation band.

## Anti-patterns (renderer should reject)

1. **Currency without non-breaking space.** Every CHF figure must read
   `CHF&nbsp;4.2&nbsp;M` or `CHF&nbsp;1&nbsp;234&nbsp;567`. A renderer that
   emits `CHF4.2M` or `CHF 4.2M` with a regular space breaks at the wrong
   column on phones and in print. The XLSX number format pin enforces this
   on the spreadsheet side; HTML templates use `&nbsp;` literals.
2. **Pillar palette on a sector table.** PROSPER pillar tints belong to
   charts. Sector exposure rows use the NOGA palette declared in
   `tokens.json` (`color.noga.A` through `color.noga.U`). Mixing the two
   creates a visual "is this a pillar score or a sector?" ambiguity.
3. **Colour-only severity.** Impact bands use both a tint and a label
   (`<CHF&nbsp;100k`, `100k–1M`, `1M–10M`, `>10M`). A board member printing
   in B/W or living with deuteranopia reads the label, not the tint.
4. **Variable headline width.** Recommendation band stretches the full
   page width every time. Squeezing it to a centred 60% column breaks the
   "decision sits at the bottom" reading expectation set by McKinsey 1-pager.

## Typography conventions

| Surface | Heading | Body | Numerals |
|---|---|---|---|
| A4 print | Inter 18/12/10pt | Inter 10pt / 1.40 | Inter Mono `tnum 1, lnum 1` |
| Web echo | Inter 20/14/11pt | Inter 15px / 1.45 | Inter Mono |
| PPTX board slide | Inter 22pt title, 14pt body | Inter Mono 14pt for CHF | Tabular |
| Email body | Arial fallback inline | Arial 13px inline | Courier New for CHF |
| XLSX | Inter 14/11pt | Inter 11pt | Consolas for figures |

### When to use Inter Mono for figures

- Always for CHF amounts inside risk cards, lever cards, the recommendation
  band's KPI inset, and every cell in the XLSX Inputs/Calculations/Output
  sheets.
- Never for prose — only for tabular figures and percentages.
- The mono cut keeps columns of CHF values visually aligned even when the
  underlying number length differs (CHF&nbsp;4.2&nbsp;M vs.
  CHF&nbsp;420&nbsp;000).

### NOGA coding rules

- Every sector-exposure row carries a single-letter division code
  (A through U per NOGA 2008) in the leftmost column.
- The row tint is keyed to the division code via the `color.noga.*` token.
- Renderers must NOT invent codes — only the 21 official NOGA divisions.
- Group-level codes (e.g. `64.19`, `35.11`) belong in the row label,
  never in the tint key.

### Swiss multilingual conventions (mandatory)

- All German output uses `ss`, never `ß` (Swiss federal admin standard).
- Non-breaking spaces before `:`, `;`, `!`, `?`, `%`, `CHF`, `°C`.
- French strings use `« »` quotes with internal non-breaking spaces.
- Dates render as `dd.mm.yyyy` (Swiss federal default).

## Accessibility floor (WCAG 2.1 AAA where practical, AA mandatory)

- Body contrast: ink `#111827` on white = **16.9:1** (AAA).
- Caption muted `#374151` on white = **10.4:1** (AAA).
- Recommendation band: navy `#1B2A4A` on gold `#C9A84C` = **7.45:1** (AAA).
- Impact band tints all maintain body-ink contrast above **15:1**.
- NOGA row tints keep body-ink contrast above **14:1** (low-saturation by design).
- Tagged PDF UA-1 wired in via the renderer.
- Tables get a `<caption>` and `<thead scope="col">`.
- A skip-link points at `#main` for keyboard users.

## Channel matrix

| Channel | Template |
|---|---|
| `pdf_a4` / `print_a4` | `risk_memo.html.j2` + `print_a4.css` |
| `web_inline` / `web_article` | `web_inline.html.j2` (noindex) |
| `email_body`          | `email_body.html.j2` |
| `pptx_slide_16_9`     | `pptx/build_pptx.py` |
| `xlsx_data`           | `xlsx/build_xlsx.py` |
| `csv_data`            | shared `csv_export.py` pattern (UTF-8 BOM) |

## Versioning

Add new tokens by extending `tokens.json` (semver minor). Removing or
renaming a token is a major bump and forces an `_v2` kit directory. Adding
a new NOGA-tint variant requires an explicit `$description` so future
renderers know which NOGA edition the colour was fixed against.
