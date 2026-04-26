# executive_dark_compact — Style Guide

**Kit ID:** `executive_dark_compact` · **Package:** `federal_councillor_v1` · **Schema:** v1.1.0
**Reference style:** Strategy& 1-pager, Confédération note de service, BCG Yellow-Note.

## When to use

This kit ships the *single-A4 hero card* a federal councillor reads in the
five minutes before stepping to the podium. Three artefacts only: the hero
card, the trajectory chart, the Q&A backgrounder. Every styling decision
protects the read-in-90-seconds promise. Use this kit whenever the
audience has executive decision authority, primary language is German, the
delivery is internal, and the document carries a personalised watermark.
Never use this kit for outward-facing artefacts — `embargoed_press`
licensing and the `noindex,nofollow` web meta are wired into every template.

## Anti-patterns (renderer should reject)

1. **Sans-serif body.** Inter is the heading family; the body is Source
   Serif 4 (Charter / Georgia fallback). Federal-grade documents use a
   serif body — it signals authority and makes 11pt readable on cream.
   Sans-serif body = visual demotion to "social card."
2. **More than one A4 of hero.** The composite + 3 KPI + recommendation must
   fit on a single A4 with 16mm margins. If overflow occurs, the renderer
   rejects rather than spilling — the executive opens a 2-page hero and
   defaults to skim-mode, which kills the aim.
3. **Coloured fills inside KPI tiles.** Tiles are white-on-cream with a
   2pt gold left border. Never fill a tile with a "good/bad" colour — the
   tabular comparison is across pillars, not within them. Severity goes in
   the trajectory chart, not in the KPI band.

## Typography conventions

| Surface | Heading | Body | Numerals |
|---|---|---|---|
| A4 print | Inter 18/13/10pt | Source Serif 4 11pt / 1.40 | Tabular lining `tnum 1, lnum 1` |
| Web echo | Inter 22/17/14px | Source Serif 4 16px / 1.40 | Tabular lining |
| PPTX hero | Inter 14pt header | Source Serif 4 18pt headline, 88pt composite | Tabular lining |
| Email body | Inter inline | Georgia (PPTX-safe fallback) 14px | Tabular lining |

The composite score is set in 64-88pt — large enough to read at 1m
under podium light. Letter-spacing -0.03em prevents the figure from
breathing too wide against the cream surface.

### Swiss German + multilingual conventions (mandatory)

- All German output uses `ss`, never `ß` (Swiss federal admin standard).
- Non-breaking spaces before `:`, `;`, `!`, `?` and units: `42 %`, `5 CHF`.
- French strings use `« »` quotes with internal non-breaking spaces.
- Italian strings follow the same `:` / `;` / `!` / `?` non-breaking rule.
- Dates render as `dd.mm.yyyy` (Swiss federal default), not `yyyy-mm-dd`.

## Accessibility floor (WCAG 2.1 AAA)

- Body contrast: ink `#0F1A30` on cream `#F2EBDA` = **14.2:1** (AAA).
- Muted body `#3D4257` on cream = **8.7:1** (still AAA).
- Navy `#1B2A4A` on cream = **12.4:1** (AAA).
- Gold `#C9A84C` is **never used as a text colour** — only as a 2-3pt
  vertical accent on KPI tiles and the recommendation band, where its
  decorative role bypasses the body-text contrast requirement.
- Tagged PDF UA-1 is wired in via the renderer; cells carry roles.
- Recommendation band uses a yellow-cream highlight `#FFF6CC` —
  contrast with body ink `#0F1A30` is **17.8:1** (AAA).
- Personalised watermark sits at 8% opacity navy — verified to remain
  invisible to OCR but present in printout for leak tracing.

## Alignment with Swiss CD + GOV.UK audience-first

- One job per page (read-aloud-able in 90 seconds) — mirrors the
  Confédération "fiche-rédacteur" 1-page convention.
- Ordering is **Composite → KPIs → Recommendation** — the scanning order
  a councillor uses to walk to the podium.
- Header brand left, topic centre, date right — same hierarchy as the
  ChF "Note de séance" template.
- Audit URL printed in every footer (transparency obligation under
  ASTRA / FOI guidance).

## PPTX channel

`build_pptx.py` produces a single 16:9 slide from `master.json` plus a
context dict. The script is deterministic — same context bytes produce
byte-identical .pptx (via python-pptx's stable XML ordering). Run with:

```
python build_pptx.py --context fixture.json --out hero.pptx
```

The composite value is centre-anchored at 88pt body weight 700 with
tabular figures — projects legibly to a 4m screen at 1080p.

## Channel matrix

| Channel | Template |
|---|---|
| `pdf_a4` / `print_a4` | `executive_brief.html.j2` + `print_a4.css` |
| `web_inline`          | `web_inline.html.j2` (noindex) |
| `docx_briefing`       | derived from `executive_brief.html.j2` via pandoc |
| internal email        | `email_body.html.j2` |
| board hero (PPTX)     | `pptx/build_pptx.py` |

## Versioning

Add new tokens by extending `tokens.json` (semver minor). Removing or
renaming a token is a major bump and forces a `_v2` kit directory.
