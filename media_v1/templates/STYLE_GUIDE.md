# editorial_press_v1 — Style Guide

**Kit ID:** `editorial_press_v1` · **Package:** `media_v1` · **Schema:** v1.1.0
**Reference style:** FT Visual Stories, Reuters wire kit, AP Stylebook, Bloomberg press visuals.

## When to use

This kit ships every artefact a Swiss federal newsroom journalist needs to
file a story before deadline: an embargoed press release, ten quotable lines
with attribution, a chart pack of transparent-background visuals (PNG + SVG
for newsroom CMS drop-in), an embargo card, an oEmbed JSON response for
third-party embeds, and a single-source-per-slide PPTX chart-pack deck. The
register is wire-service neutral: Inter heading, Source Serif 4 body, no
promotional vocabulary, no buried lede. Use this kit for any journalist or
newsroom audience. Never use it for internal briefings — those have their
own kits.

## Anti-patterns (renderer should reject)

1. **Coloured chart backgrounds.** Press charts are transparent so the host
   newsroom CMS controls the surface. A renderer that bakes a white or cream
   panel into the PNG defeats the entire chart-pack contract. The token
   `data.chart_bg` is locked to `"transparent"` for that reason.
2. **Headlines over 80 characters or ledes over 30 words.** These are
   wire-service hard limits, declared in `tokens.json` as
   `typography.max_headline_chars` and `typography.max_lede_words`. The
   renderer must reject overflow before pre-flight rather than truncate.
3. **Embargo red outside the embargo channel.** `--press-embargo-red` is
   reserved for the embargo banner, watermark and embargo card. Using it on
   a chart series, a pull-quote bar or a confidence badge mixes "legal
   warning" semantics with editorial hierarchy and breaks newsroom trust.
4. **Promotional language.** Words like "groundbreaking", "innovative",
   "exclusive", "first-ever" are flagged by the QA gate
   `no_promotional_drift` (declared in `package_spec.json`).

## Typography conventions

| Surface | Heading | Body | Numerals |
|---|---|---|---|
| Web / press release | Inter 40/22/17px | Source Serif 4 16px / 1.55 | Tabular lining `tnum 1, lnum 1` |
| A4 print            | Inter 28/14/11pt | Source Serif 4 11pt / 1.45 | Tabular lining |
| PPTX chart slide    | Inter 26pt title  | Source Serif 4 14pt subtitle | Tabular lining |
| Email body          | Arial fallback inline | Georgia inline | Tabular lining |
| Pull-quote          | n/a               | Source Serif 4 24px italic | Lining |

The lede sits one notch heavier than body (`font-weight: medium`) — the FT
convention that lets the lede pull the eye without competing with the
headline. Confidence badges use Inter 10px uppercase, semi-bold, on solid
colour backgrounds keyed to the verdict (high green, medium gold, low gray,
contested red).

### Swiss multilingual conventions (mandatory)

- All German output uses `ss`, never `ß` (Swiss federal admin standard).
- Non-breaking spaces before `:`, `;`, `!`, `?`, `%`, `CHF`, `°C`.
- French strings use `« »` quotes with internal non-breaking spaces.
- Italian strings follow the same `:` / `;` / `!` / `?` non-breaking rule.
- Datelines in CITY uppercase per AP convention: `BERN, 26.04.2026 —`.
- Time zones always cited explicitly (`CET`, `CEST`) on every embargo string.

## Embargo handling

- Banner appears at the top of every artefact during the embargo window.
- A diagonal `EMBARGOED` watermark at 12% opacity sits behind body text.
- `noindex,nofollow` is wired into the `<head>` of every embargoed artefact.
- The embargo card carries release time, lift time, contact window, and
  three free-text conditions — printed independently of the release itself.
- `embargo_red` token use is restricted to embargo-context elements only;
  the linter scans `kit.css` for forbidden uses.

## Watermark policy

- `embargoed`: diagonal red `EMBARGOED` at 12% opacity.
- `clean`: no watermark, used post-release.
- The body class `watermarked` toggles the visual via CSS — the template
  reads `embargo` truthiness from context and adds the class accordingly.
- Watermark is text-based (not a raster overlay) so screen-readers and
  print-OCR pick it up unambiguously.

## Accessibility floor (WCAG 2.1 AA)

- Body contrast: ink `#0E1320` on white = **17.9:1** (AAA).
- Caption muted `#3F4A5C` on white = **9.1:1** (AAA).
- Byline `#6B7280` on white = **4.8:1** (AA — this is the floor; only used
  for non-essential metadata).
- Embargo banner: white on `#B91C1C` = **6.7:1** (AA-large; also AA-body).
- Pull-quote gold bar `#C9A84C` is decorative only — never used as text.
- `aria-label` on the embargo banner; `<figure>` + `<figcaption>` on every
  chart row; `alt` on every image (renderer-enforced when
  `accessibility.alt_text_required: true`).
- A skip-link points at `#main` for keyboard users.

## Channel matrix

| Channel | Template |
|---|---|
| `pdf_a4` / `print_a4` | `press_release.html.j2` + `print_a4.css` |
| `web_article`         | `press_release.html.j2` (or `quotables` / `chart_pack`) |
| `web_inline`          | `web_inline.html.j2` (base) |
| `email_body`          | inline-styled press release (rendered upstream) |
| `csv_data`            | quotable + claim_id table (via shared csv_export pattern) |
| `oembed`              | `oembed_response.json.j2` |
| chart deck (PPTX)     | `pptx/build_pptx.py` |

## Versioning

Add new tokens by extending `tokens.json` (semver minor). Removing or
renaming a token is a major bump and forces an `_v2` kit directory.
