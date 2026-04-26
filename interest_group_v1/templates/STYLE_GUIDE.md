# federation_flexible_v1 — Style Guide

**Kit ID:** `federation_flexible_v1` · **Package:** `interest_group_v1` · **Schema:** v1.1.0
**Reference style:** Schweizer Bauernverband (USP) member newsletter, Schweizerischer Gewerkschaftsbund (SGB) Mitgliederzeitung, pro Senectute "Generation 60+" newsletter.

## When to use

This kit ships every artefact a federation communications team needs to
turn a PTT analysis into the next member newsletter, member email, sector
impact card, and 90-second audio summary for the federation's WhatsApp
channel. Federations are heterogeneous — agriculture (USP), unions (SGB),
seniors (pro Senectute) speak with very different vocal registers, so the
kit is built around a shared base palette + three swap-in palettes. The
content register stays the same regardless of palette: explanatory advocacy,
plain-language framing of the sector cut, and a clear "what this means for
our members" call-to-action. The federation's own voice is preserved by
restraint — we never speak FOR the federation, only ABOUT impact ON its
members.

## Anti-patterns (renderer should reject)

1. **Speaking FOR the federation.** A line like "USP demands a moratorium"
   is forbidden. The PTT platform never puts words in a federation's mouth.
   Render text as: "An eight-month moratorium would protect 47% of dairy
   smallholders from the worst-case scenario" — leaving the demand to the
   federation. The QA gate `false_attribution` enforces this.
2. **Mixing palettes within one artefact.** A newsletter is rendered with
   exactly one `data-palette` value. Renderers must NOT compose
   `accent` from one palette with `cta` from another. This produces
   federation-confusing visuals and breaks brand independence.
3. **Body text below 17px on web / 11pt in print.** Federation members
   skew older. The minimum body-text floor is one notch above the other
   kits. The pro Senectute palette pushes that further to 19px / 12pt.
4. **Heroic statistics without source labels.** Every `fed-hero__stat`
   must be paired with a source label in the surrounding paragraph or the
   `member_impact_card` source line. Stat without source breaks the
   "transparent advocacy" contract that federation comms departments rely on.

## Typography conventions

| Surface | Heading | Body | Numerals |
|---|---|---|---|
| Web   | Inter 32/22/18px | Source Serif 4 17px / 1.55 (pro_senectute: 19px / 1.65) | Lining `lnum 1` |
| Print A4 | Inter 20/14/12pt | Source Serif 4 11pt / 1.55 | Lining |
| Email body | Arial inline (Outlook-safe) | Georgia inline 17px | Arial for figures |
| Audio (TTS) | n/a — plain prose | period/comma punctuation only | n/a |

Hero stats sit at 56px web / 36px email — large enough to anchor a
member's scroll-stop, small enough to coexist with serif body. Tabular
numerals are NOT used in this kit — federations prefer lining figures
because the newsletter register reads more like a magazine than a board pack.

### Palette swap mechanics

- The palette is selected via `data-palette="usp|sgb|pro_senectute"` on
  `<html>` or `<body>`. Default (`base`) applies if the attribute is
  absent.
- All palette-aware tokens are CSS custom properties prefixed `--fed-*`
  in `kit.css`. The `[data-palette="..."]` selectors reassign those
  properties at the root level — no template duplication needed.
- The Outlook-safe `email_body.html.j2` resolves palette colours inline
  (Outlook ignores CSS variables) by looking up a Jinja dict keyed by
  the palette identifier.
- Federation logos sit in a 64×64 placeholder tile (`.fed-masthead__logo`)
  filled with the per-palette `accent_soft` colour. Renderers can replace
  the placeholder with an `<img>` carrying `alt="<federation> Logo"`
  without altering CSS.

### Swiss multilingual conventions (mandatory)

- All German output uses `ss`, never `ß` (Swiss federal admin standard).
- Non-breaking spaces before `:`, `;`, `!`, `?`, `%`, `CHF`, `°C`.
- French strings use `« »` quotes with internal non-breaking spaces.
- Italian strings follow the same `:` / `;` / `!` / `?` non-breaking rule.
- Audio scripts use period+comma punctuation only — TTS engines pace
  more naturally on those than on dashes.

## Accessibility floor (WCAG 2.1 AAA where practical)

- Body contrast (base): ink `#1F2937` on paper `#FAFAF7` = **13.6:1** (AAA).
- USP palette: walnut `#2A2418` on earth-paper `#F4EFE6` = **13.0:1** (AAA).
- SGB palette: black `#0A0A0A` on white = **19.3:1** (AAA).
- pro Senectute palette: black `#111827` on cream `#FEFAEE` = **16.4:1** (AAA).
- Every accent colour was selected to clear **5.5:1** on white minimum
  (USP green 5.5, SGB red 6.7, teal 5.7, gold 7.1).
- Touch targets ≥ 48×48px (raised from the 44px floor — older audiences).
- A skip-link points at `#main` for keyboard users.
- `prefers-reduced-motion: reduce` collapses every transition.

## What NOT to do

- Do not ventriloquise. We render impact, not stance.
- Do not invent federation positions. The `federation_quote` template
  field carries factual statements — never policy demands.
- Do not blend palettes. One artefact = one palette.
- Do not shrink body text. The 17px / 11pt floor is for member retention.

## Channel matrix

| Channel | Template |
|---|---|
| `pdf_a4` / `print_a4` | `newsletter.html.j2` + `print_a4.css` |
| `web_inline` / `web_article` | `web_inline.html.j2` (noindex) |
| `html_newsletter`     | `newsletter.html.j2` |
| `email_body`          | `email_body.html.j2` (palette-resolved inline) |
| `member_impact_card`  | `member_impact_card.html.j2` (include or standalone) |
| `audio_summary`       | `audio_script.txt.j2` (90s TTS-ready) |
| `png_chart`           | rendered separately, dropped into `<figure>` blocks |

## Versioning

Add new federation palettes by extending `tokens.json` (semver minor).
Removing or renaming a palette is a major bump. New palettes must declare
explicit contrast figures in the `$description` field per the AAA-aware
review checklist.
