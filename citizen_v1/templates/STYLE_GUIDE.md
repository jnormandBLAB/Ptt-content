# citizen_civic_warm — Style Guide

**Kit ID:** `citizen_civic_warm` · **Package:** `citizen_v1` · **Schema:** v1.1.0
**Reference style:** Swiss federal voting brochure 2024, WHO-Europe public-info posters, GOV.UK voter cards.

## When to use

This kit ships every artefact a citizen sees in their letterbox, on a
WhatsApp forward, on a Story, or via the audio summary on the bus to the
polling station. The whole kit is built around **one job**: stop the
scrolling thumb in under one second, then deliver three facts in two minutes
without talking down. Use the Civic Warm tonality (warm-white surface
`#FBF7EE`, cream hero `#F4ECD8`) whenever the audience is the general public
voting on a federal or cantonal question. Do not use this kit for
embargoed press, executive briefings, or business-tactical reports — those
have their own kits.

## Anti-patterns (renderer should reject)

1. **Eight-axis chart.** Governance (P8) is a multiplier, never a chart axis.
   The 7-pillar invariant holds across every visual in this kit. A spider
   with eight spokes is a hard fail.
2. **Inline hex colours in any template.** All colour comes from
   `tokens.json` via the CSS custom properties declared in `kit.css`.
   Adding a one-off `style="color:#abc"` is a fail — extend the token kit
   instead, then bump the `$version` in `tokens.json`.
3. **Italic body for emphasis.** Italic disappears at 18px on phones and at
   11pt on warm paper stock. Use `font-weight: var(--fw-semibold)` (600)
   instead. Italic is reserved for foreign-language quotes and titles of works.

## Typography conventions

| Surface | Heading | Body | Numerals |
|---|---|---|---|
| Web   | Inter 32/24/20 | Inter 18px / 1.55 | Tabular lining (`tnum 1, lnum 1`) |
| Print A5 | Inter 22/14/12pt | 11pt / 1.45 | Tabular lining |
| Social | Inter 240/180/88px depending on canvas | n/a | Tabular lining, `letter-spacing: -0.04em` |

Hero shock-stats use a custom 72-240px display weight 800. Captions never
exceed 36px on the 1080x1080 canvas.

### Swiss French typographic conventions (mandatory)

- Quotation marks use `« »` with a non-breaking space inside: `« exemple »`.
- Non-breaking space (`&nbsp;` in HTML, ` ` in JSON) **before** every
  `%`, `CHF`, `°C`, `:`, `;`, `!`, `?`. Example: `42&nbsp;%`, `Vote&nbsp;:`.
- Apostrophes use the typographic `’` (U+2019), not the typewriter `'`.
- Numbers use a thin space as thousands separator: `1 234 567`.
- For German output, every `ß` becomes `ss` (Swiss federal admin standard).

## Accessibility floor (WCAG 2.1 AA)

- Body text contrast: navy `#1B2A4A` on warm-white `#FBF7EE` = **9.1:1**
  (exceeds 4.5:1 floor).
- Body text on cream `#F4ECD8` = **8.4:1**.
- Caption muted `#5A5040` on cream = **7.2:1** (still AAA).
- Gold `#C9A84C` is **only used as a background with navy text** — gold on
  white falls below 4.5:1 and is forbidden for text.
- Touch targets ≥ 44×44px (audio control, share buttons, FAQ summaries).
- All images carry `alt` text in the artefact's primary language.
- Focus ring: 3px gold halo (`--sh-ring`) on every interactive element.
- `prefers-reduced-motion: reduce` collapses every transition to ~0ms.
- A skip-link points at `#main` for keyboard users.

## Alignment with Swiss CD + GOV.UK audience-first

- Plain language register (FALC-adjacent, B1 CEFR target) per
  `every_voices_meta.plain_language` in `package_spec.json`.
- One aim per page (decide & explain) — no upsell, no related-topic carousel.
- Audit link visible in the footer of every artefact (transparency is the
  point — see GOV.UK's "show your working" pattern).
- The vote-date pill is always the first visible element on every artefact
  (Swiss CD: anchor on the act, not the brand).

## Channel matrix

| Channel | Template | Notes |
|---|---|---|
| `web_inline` / `web_article` | `web_inline.html.j2` | Default landing page |
| `social_square_1080` | `social_square_1080.html.j2` | Instagram, LinkedIn |
| `social_landscape_1200x630` | `social_landscape_1200x630.html.j2` | OG / Twitter share |
| `social_story_1080x1920` | `social_story_1080x1920.html.j2` | IG / WA Status |
| `whatsapp_card` | `whatsapp_card.html.j2` | Forwarded to friend |
| `email_body` (newsletter) | `email_body.html.j2` | 600px table layout |
| `pdf_a5` / `print_a5` | `web_inline.html.j2` + `print_a5.css` | Letterbox drop |
| `audio_summary_90s` | TTS via `audio.tts_swiss_voices_v1` | Companion transcript on web |

## Versioning

Add new tokens by extending `tokens.json` (semver minor). Removing or
renaming a token is a major bump and forces a new `_v2` kit directory —
mirror the package-level supersession policy.
