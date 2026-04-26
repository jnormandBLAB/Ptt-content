# parliamentary_classic — Style Guide

**Kit ID:** `parliamentary_classic` · **Package:** `policy_advisor_v1` · **Schema:** v1.1.0
**Reference style:** UK Cabinet Office One-Page Brief, Bundeskanzlei Botschaftsformat, Federal Chancellery "note d'analyse", Greffe du Conseil federal dossier.

## When to use

This kit ships the artefacts a parliamentary policy advisor (Wissenschaftliche
Mitarbeiterin Generalsekretariat, conseiller scientifique au Greffe) needs to
brief a councillor's office or a parliamentary commission staff before a
committee session. Four canonical artefacts: the parliamentary brief itself
(4 pages dense), the lever x actor x horizon CSV matrix that translates
analysis into actionable amendments, the Q&A pack the councillor's spokesperson
walks into the room with, and the side-by-side legal diff that lets a
commission member read a proposed amendment against the current Cst./LPE/LRTV
article in three columns. Use this kit when the audience reads serif at 10pt
and expects every figure footnoted.

## Anti-patterns (renderer should reject)

1. **Sans-serif body.** The whole register is federal-serif. Inter on the
   body collapses the document into "consulting deck" tone. The body remains
   Source Serif 4 (Charter, Georgia fallbacks). Headings also serif here —
   different from the executive kit which uses Inter for headings.
2. **Narrow margins under 18 mm.** Parliamentary brokers annotate in the
   margin. Print margin is 20 mm, never tighter. A renderer that tries to
   pack content edge-to-edge to fit one page must instead break to a second
   page rather than steal the gutter.
3. **Coloured pillar bars in a Cst./LPE diff.** The diff grid only carries
   semantic add/del/mod tints (`--parl-diff-add/del/mod`). Tinting a column
   with the PROSPER pillar palette mixes two semantic systems and is rejected.

## Typography conventions

| Surface | Heading | Body | Numerals |
|---|---|---|---|
| A4 print | Source Serif 4 18/13/11pt | Source Serif 4 10pt / 1.40 | Tabular lining `tnum 1, lnum 1` |
| Web echo | Source Serif 4 24/18/15px | Source Serif 4 15px / 1.45 | Tabular lining |
| PPTX briefing | Source Serif 4 18-32pt | Source Serif 4 14pt | Tabular lining |
| Email body | Georgia (PPTX-safe fallback) 14px | Georgia 14px | Tabular lining |
| Article citations | Source Serif 4 italic, `« »` quotes | Inline | n/a |

Article-citation runs (e.g. `art. 8 al. 2 LPE`) are wrapped in the
`.legal-cite` span which adds `« »` and italicises — making them visually
distinct from claim references.

### Swiss multilingual conventions (mandatory)

- All German output uses `ss`, never `ß` (Swiss federal admin standard).
- Non-breaking spaces before `:`, `;`, `!`, `?`, `%`, `CHF`, `°C`.
- French strings use `« »` quotes with internal non-breaking spaces.
- Italian strings follow the same `:` / `;` / `!` / `?` non-breaking rule.
- Dates render as `dd.mm.yyyy` (Swiss federal default).
- Article citations stay in the original act's language (a French commission
  paper still cites `art. 8 al. 2 LPE`, not `Umweltschutzgesetz Art. 8 Abs. 2`).

## Accessibility floor (WCAG 2.1 AAA where practical, AA mandatory)

- Body contrast: ink `#10182B` on paper `#FDFCF7` = **17.4:1** (AAA).
- Muted body `#46505F` on paper = **8.4:1** (AAA).
- Annotation badge: gold `#7A6A24` on white = **7.1:1** (AAA).
- Diff backgrounds (`#E2EFE6` add, `#F8E5E5` del, `#FFF6CC` mod) all keep
  body ink contrast above **15:1**.
- Tagged PDF UA-1 wired in via the renderer; table cells carry roles.
- Tables get a `<caption>` with the source citation; `<thead scope="col">`.
- A skip-link points at `#main` for keyboard users.
- `prefers-reduced-motion: reduce` collapses every transition.

## Alignment with Swiss CD + GOV.UK audience-first

- One job per artefact: brief = analysis, csv = action matrix, Q&A = podium prep.
- Audit URL footed on every page (transparency is the contract).
- `noindex,nofollow` on the web echo — these documents are working drafts.
- DRAFT watermark visible behind body text on every print page.

## Channel matrix

| Channel | Template |
|---|---|
| `pdf_a4` / `print_a4` | `web_inline.html.j2` + `print_a4.css` |
| `web_inline`          | `web_inline.html.j2` (noindex) |
| `docx_briefing`       | `docx_briefing.html.j2` (pandoc-friendly markup) |
| `csv_data`            | `csv_export.py` (UTF-8 BOM for Excel) |
| internal email        | `email_body.html.j2` |
| commission deck (PPTX)| `pptx/build_pptx.py` |

## Versioning

Add new tokens by extending `tokens.json` (semver minor). Removing or
renaming a token is a major bump and forces a `_v2` kit directory.
