# PTT Stakeholder Packages

This directory contains the **content contracts** that drive every artefact the
PTT Platform delivers — today as a directory bundle (PDF / DOCX / HTML / MD /
SVG / PNG / PPTX), tomorrow as the **Every Voices** multi-stakeholder web
platform.

One `package_spec.json` per stakeholder. One contract. One source of truth.

---

## Layout

```
packages/
  _schema/
    package_spec.schema.json     # JSON Schema draft 2020-12 — the contract
    aim_test_examples.md          # 6 worked examples of aim_test rubrics
    adapter_refactor.md           # how to refactor src/ptt_stakeholder_adapter
  citizen_v1/package_spec.json
  federal_councillor_v1/package_spec.json
  policy_advisor_v1/package_spec.json
  media_v1/package_spec.json
  entrepreneur_v1/package_spec.json
  interest_group_v1/package_spec.json
```

A package is a **directory** named `{stakeholder_id}_v{major}/`. Today it
contains only `package_spec.json`. Tomorrow the Every Voices CMS may add
`overrides/`, `assets/`, or `localised_strings/` siblings without changing
the schema (additive evolution — see the semver policy below).

---

## Design principles (the eight non-negotiables)

1. **Aim-driven, not shape-driven.** The old adapter produced a 4 audiences ×
   5 cell-types matrix — 20 cookie-cutter cells. That model treats every
   reader as a column in a spreadsheet. The new model treats each stakeholder
   as a person with **one aim** and ships exactly the artefacts that aim
   needs. New stakeholder = new `package_spec.json`. No code.

2. **Web-first, multi-channel.** Every artefact declares the channels it can
   ship on — `web_inline`, `pdf_a4`, `social_square_1080`, `whatsapp_card`,
   `audio_summary_90s`, `falc_simplified`, `large_print_a4`, `oembed`, etc.
   The renderer dispatches per channel. Same artefact, many surfaces, no
   duplication.

3. **Multi-language native.** FR / DE (`ss` not `ß`) / IT / RM. Storage is
   language-neutral; every i18n string is a `{lang_code: str}` map at the
   leaf. Translation happens at render time only, per the project's
   [`/.claude/rules/i18n.md`](../.claude/rules/i18n.md).

4. **Accessibility baked in.** Each artefact declares `wcag_level`,
   `alt_text_required`, `tagged_pdf_ua1`, `min_contrast_ratio`,
   `falc_variant`, `large_print_variant`. The renderer **fails** the artefact
   if any required commitment cannot be fulfilled — never silently downgraded.

5. **Aim-test as the ultimate QA gate.** Each package declares an `aim_test`:
   "If a typical stakeholder reads ONLY this package, can they complete
   their aim?" A rubric with weighted criteria scores the package on a 0-1
   scale. This **supersedes** the technical-only gates (`non_empty`,
   `min_length`, `coherent`) — those still run, but they no longer ship the
   package on their own.

6. **Schema.org / JSON-LD aware.** Every artefact carries a
   `schema_org.type` (`Article`, `ClaimReview`, `Report`, `Dataset`, ...).
   `ClaimReview` triggers Google Fact Check Tools indexing — which is how
   verified claims surface in search results.

7. **Provenance-aware.** Each artefact carries `provenance_hooks` that
   reconnect the artefact to the EKB audit chain (claim → evidence →
   source → query). The orchestrator emits `ADAPTER_RENDERED` events
   referencing these hooks so the audit trail survives publication.

8. **Stable + evolvable.** `schema_version: 1.0.0` follows semver. Adding a
   new optional field is a **minor** bump. Removing or renaming a field is a
   **major** bump. Anything you can't fit in the schema lives under the
   `extensions.{vendor}` namespace and the validator does not gate it.

---

## How to add a new stakeholder package

1. Pick a stable `stakeholder_id` (snake_case, ≤ 40 chars). Examples:
   `cantonal_official`, `ngo_advocate`, `young_voter`, `expat`.
2. Write the **aim** in one sentence per language. Action verb first.
   Time-bounded if applicable. The aim is the entire reason the package
   exists — if you can't write it, the package doesn't exist.
3. Pick **3-7 artefacts** that, together, let the stakeholder fulfil the aim.
   Less is more. The schema caps you at 12 artefacts; in practice 5 is
   usually right.
4. For each artefact, set `format`, `renderer`, `channels`, `accessibility`,
   `provenance_hooks`, `schema_org`. Reuse renderer ids — adding a new
   renderer means adding code; reusing one means adding config.
5. Write the `aim_test` rubric: 3-8 criteria, each with a `pass_signal_i18n`
   stating concrete observable evidence. `min_score` defaults to `0.8`;
   raise it to `0.85+` for executive-grade packages.
6. Set `every_voices_meta` — at minimum `url_slug_template`,
   `schema_org_type`, `subscription_topic`. Forward-portability is the whole
   point of this block.
7. Validate against the schema:
   `python -m jsonschema -i packages/your_v1/package_spec.json packages/_schema/package_spec.schema.json`
8. Run the renderer dry-run:
   `python -m ptt_stakeholder_adapter.run --package your_v1 --dry-run --report fixtures/sample.json`

---

## Semver evolution policy

| Change | Bump | Rationale |
|---|---|---|
| Add an OPTIONAL field to schema | minor (`1.0.0` → `1.1.0`) | Old packages still validate. |
| Add a REQUIRED field to schema | major (`1.0.0` → `2.0.0`) | Old packages fail validation. |
| Rename or remove a field | major | Breaks every consumer. |
| Add a new enum value to an open enum (`channel`, `format`) | minor | Existing values unaffected. |
| Add a new enum value to a closed enum (`stance`, `register`) | major | Closed enums are part of the public contract. |
| Add a field under `extensions.{vendor}` | none | Extensions namespace is unbounded by design. |

A package's `schema_version` MUST match the major version of the schema it is
validated against. Renderers dispatch on `(major, minor)` — `package_spec`
files MAY use a lower minor than the renderer (forward compatible) but never
a higher one.

When a package is materially redesigned (different aim, different artefact
set, different look-and-feel), do not bump in place — issue a new
`{stakeholder}_v2/` directory and add `"supersedes": "{stakeholder}_v1"` to
the new spec. The Every Voices CMS handles the 301 redirect automatically.

---

## The Every Voices forward-portability story

Today's adapter renders a directory of files for one report. Tomorrow's
Every Voices platform renders the **same** packages onto the open web — with
RSS, oEmbed, JSON-LD, subscriptions, share-cards, audio summaries, FALC
variants, large-print variants, and per-canton personalisation.

The platform refactor is a **config change**, not a code change, because:

- `every_voices_meta.url_slug_template` already defines the canonical URL.
- `every_voices_meta.schema_org_type` already declares the JSON-LD page type.
- `every_voices_meta.rss_eligible` and `subscription_topic` already wire the
  package into the subscription engine.
- `every_voices_meta.og_image_artefact_ref` already points at the share image.
- `every_voices_meta.tts_eligible`, `falc_eligible`, `large_print_eligible`
  already authorise the accessibility variants.
- `every_voices_meta.personalisation_keys` already declares which dimensions
  the platform may use to re-rank artefacts within the package — and
  excludes everything else.
- Each artefact's `channels[]` already includes web channels alongside the
  PDF channels, so the renderer registry only needs to bind a web renderer
  to the existing artefact ids.

Today these fields are read by exactly zero code paths in the directory
adapter. Tomorrow they become the platform's primary contract. That is the
forward-portability promise: the schema is **right** today even though it is
only **partly used** today.

---

## v1.1.0 — Forward-portability fields (Every Voices contract)

Schema **v1.1.0** is a backwards-compatible additive bump that promotes
`every_voices_meta` from a thin set of eligibility flags to a full forward
contract with the Every Voices web platform. v1.0.0 instances continue to
validate unchanged — every new field is optional. The six new sub-objects
are detail-when-eligible: each elaborates an existing flag (`tts_eligible`,
`falc_eligible`, etc.) with the platform-specific knobs the consumer needs.

| Sub-object | Purpose | Platform consumer |
|---|---|---|
| `every_voices_meta.web` | Multi-language URL siblings (`hreflang`) and the canonical pointer. Lets the Astro layer emit `<link rel="alternate" hreflang="...">` tags and the canonical URL without re-deriving paths from `url_slug_template`. Mark RM (or any rare language) as `optional: true` so the discovery worker tolerates missing translations. | **Astro 5** (sitemap + hreflang + canonical) |
| `every_voices_meta.tts` | Per-language neural voice ids (Azure Cognitive Services convention `xx-XX-NameNeural`), target spoken duration, the source artefact whose rendered text feeds the synthesiser, embed targets, and the WCAG transcript baseline. Required when `tts_eligible: true`. | **Azure Speech Switzerland North** + the audio renderer (`audio.tts_swiss_voices_v1`) |
| `every_voices_meta.plain_language` | CEFR target (B1 default), the base artefact that gets a FALC twin, sentence/syllable hard limits, pictogram authorisation, and the post-render lint chain. Required when `falc_eligible: true`. | The FALC simplification editor + `language_tool_python` / `capito_score` checkers |
| `every_voices_meta.analytics` | Cookie-less Plausible custom-prop tagging. Closed enum of events the renderer must instrument (`package_view`, `artefact_open`, `share_clicked`, `subscription_signup`, `audio_played`, `download_clicked`, `embed_loaded`, `push_opened`, `audit_link_clicked`). Stakeholder + topic cohorts decouple the analytics taxonomy from the stakeholder id. | **Plausible self-hosted** (Switzerland-resident instance) |
| `every_voices_meta.push` | Eligible transports (`web_push`, `telegram`, `whatsapp_broadcast`, `email_alert`, `matrix`), broker channel key, priority, per-subscriber weekly rate limit, headline source artefact, and embargo behaviour. Defaults to follow `delivery.embargo_aware` for press packages. | **Listmonk** + per-transport adapters (web-push, Telegram Bot API, WhatsApp Business, SMTP) |
| `every_voices_meta.provenance` | Top-level audit URL template (paired with the per-artefact `provenance_hooks`), per-claim ClaimReview JSON-LD endpoint, license id (mirrors `delivery.share_policy.license`), and toggles for whether the audit footer ships in PDFs and as JSON-LD in HTML. This is the bridge that lets a citizen click any artefact and reach the full claim → evidence → source → query DAG. | **Every Voices audit page** (Astro route `/audit/{report_id}`) + Google Fact Check Tools indexing via the ClaimReview endpoint |

In addition, the **artefact-level** `schema_org` block gained one optional
field: `claim_reviews_from`, with values `"claim_ids"`, `"explicit"`, or
`"none"`. When set, the renderer attaches one
[`schema.org/ClaimReview`](https://schema.org/ClaimReview) JSON-LD block per
claim id derived via the named source. This pairs with the artefact-level
`provenance_hooks.emit_claim_review_jsonld` flag (which decides *whether*
to emit) and the package-level `provenance.claim_review_jsonld_endpoint`
(which decides *where the per-claim endpoint lives*). Together they drive
Google Fact Check Tools surfacing of every verified claim the platform
publishes.

### Why these six fields are load-bearing for Every Voices

The v1.0.0 `every_voices_meta` block answered *whether* a package is
eligible for a given Every Voices feature. v1.1.0 answers *how* the platform
should execute on that eligibility — without forcing the platform to
hard-code stakeholder-specific behaviour. Adding a stakeholder remains a
one-file change. Switching push transports, retuning FALC limits, or
swapping a TTS voice all become edits to the package_spec, never code.

### Population matrix (today's six packages)

| Package | web | tts | plain_language | analytics | push | provenance |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `citizen_v1` | yes | yes | yes | yes | yes | yes |
| `federal_councillor_v1` | yes | — | — | yes | — | yes |
| `policy_advisor_v1` | yes | — | — | yes | — | yes |
| `media_v1` | yes | — | — | yes | yes (embargo-aware urgent) | yes |
| `entrepreneur_v1` | yes | — | — | yes | yes (high) | yes |
| `interest_group_v1` | yes | yes (newsletter audio) | — | yes | yes | yes |

A dash means the package is intentionally exempt — federal-councillor briefs
are internal-only and embargoed, policy-advisor packages target a closed
ministerial audience, FALC is unnecessary for federation packages because
federations maintain their own simplified-language register, and
entrepreneur briefs are sector-tactical rather than mass-public.

---

## Cross-references

- [`.claude/rules/i18n.md`](../.claude/rules/i18n.md) — i18n storage rules
- [`.claude/rules/provenance.md`](../.claude/rules/provenance.md) — provenance event types
- [`.claude/rules/score-ranges.md`](../.claude/rules/score-ranges.md) — claim 0-5, pillar 0-100, governance 0.0-1.5
- [`.claude/rules/pydantic-patterns.md`](../.claude/rules/pydantic-patterns.md) — model conventions
- `src/ptt_stakeholder_adapter/` — current adapter (to be refactored per
  `_schema/adapter_refactor.md`)
- `src/ptt_rendering/templates/` — registered template families (resolved
  via `look_and_feel.template_ref`)
- `src/ptt_ui/config.py` — color and typography tokens

---

## SemVer bump policy (this repo)

This repo is published as the npm package `@ptt/content` to the GitHub
Packages registry. Versioning follows SemVer:

- **MAJOR** — breaking change to `_schema/package_spec.schema.json` that
  existing consumers cannot ignore (removed required field, narrowed
  enum, renamed top-level key). Coordinated with a Claude_ptt-side PR.
- **MINOR** — new optional field, new enum value, new package directory,
  schema additions that are forward-compatible.
- **PATCH** — content fixes (typos, wording, FALC tweaks), CI / docs /
  workflow changes that don't alter the contract.

Baseline is `1.0.0`. Tag a release with `git tag v1.2.3 && git push --tags`;
the `publish` workflow does the npm publish.

---

## Repo bootstrap checklist for admins

These steps must be executed manually by a repo admin **before** the
first content-team PR. The agent that bootstrapped this repo cannot do
them (they require team creation, branch-protection write, secret
provisioning).

1. **Create the `@jnormandBLAB/content-stewards` GitHub team** and assign
   at least 2 members. The `CODEOWNERS` file points at this team; PRs
   will sit unreviewable until the team exists.
2. **Branch protection on `main`**:
   - Require pull request before merging
   - **Require 2 reviewers from CODEOWNERS**
   - **Require signed commits**
   - Disallow force-push
   - Disallow admin bypass
   - Require linear history
   - Required status checks: `validate`
3. **Add three repo secrets** (Settings -> Secrets and variables ->
   Actions). Copy the values from the matching secrets in the
   `Claude_ptt` repo settings (these are the same HMAC keys the
   receiver-side Astro app validates against — they MUST match):
   - `FALC_DISPATCH_HMAC_SECRET`
   - `TTS_DISPATCH_HMAC_SECRET`
   - `PUSH_DISPATCH_HMAC_SECRET`
4. **Tag `v1.0.0`** to trigger the first npm publish:
   ```
   git tag v1.0.0
   git push origin v1.0.0
   ```
   Verify the `publish` workflow succeeds and the package shows up under
   GitHub Packages on the org.

