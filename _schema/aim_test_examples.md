# Aim-Test Worked Examples

Six examples — one per stakeholder package — showing how the
`aim_test` block is administered, what a passing trace looks like, and
what a failing trace looks like.

The aim-test is the single ultimate QA gate. The deterministic gates
(`claim_traceability`, `no_inference_beyond_evidence`, `reading_grade_match`,
...) still run, but a package only ships when **both** sets pass.

Format per example:

- **Prompt** (single sentence, mirrors `stakeholder.aim_i18n`)
- **Rubric** (criteria with weights)
- **Sample PASS trace** (judge output that ships the package)
- **Sample FAIL trace** (judge output that blocks the package + remediation)

The judge is `claude-opus-4-7@1m` for `llm_judge` and `hybrid` types. For
`human_panel`, three independent reviewers fill the same rubric and the
median weighted score is taken.

---

## 1. `citizen_v1` — type: hybrid, min_score: 0.80

**Prompt** (FR): *"Après avoir lu uniquement ce package, peux-tu (a) nommer la
date du vote, (b) citer le chiffre-choc et (c) formuler en une phrase ce que tu
dirais à un proche pour expliquer ton choix ?"*

**Rubric** (5 criteria, total weight 5.5):

| criterion_id | weight | pass signal |
|---|---|---|
| `vote_date_recall` | 1.0 | Date cited without re-reading. |
| `shock_stat_recall` | 1.0 | Figure + unit cited. |
| `explainable_to_relative` | 1.5 | One sentence intelligible to a non-expert. |
| `balance_perceived` | 1.0 | Reader cannot tell if author is pro/con. |
| `no_jargon` | 1.0 | No unexplained acronym or raw legal term. |

### PASS sample

Judge response (paraphrased):

> *vote_date_recall: PASS — Reader said "22 septembre 2026" verbatim.*
> *shock_stat_recall: PASS — Reader said "12 % de hausse des cotisations".*
> *explainable_to_relative: PASS — "Si on accepte, on paie 12 % de plus chaque mois mais l'AVS tient jusqu'en 2050."*
> *balance_perceived: PASS — "Je ne sais pas pour qui voter, mais je comprends ce qui est en jeu."*
> *no_jargon: PASS — Pas d'acronyme isolé, "AVS" expliqué dans la deuxième phrase.*

Weighted score: `5.5 / 5.5 = 1.00`. **Ships.**

### FAIL sample

Judge response:

> *vote_date_recall: PASS.*
> *shock_stat_recall: FAIL — Reader said "il y a une hausse" but couldn't cite the number.*
> *explainable_to_relative: FAIL — Reader's reformulation contained "PROSPER score" without explanation.*
> *balance_perceived: PASS.*
> *no_jargon: FAIL — Reader's reformulation lifted three uncontextualised acronyms from the brief.*

Weighted score: `(1.0 + 0 + 0 + 1.0 + 0) / 5.5 = 0.36`. **Blocks.**

**Remediation:** the brief renderer overran the citizen reading-grade and
imported framework jargon directly. The orchestrator re-runs `two_minute_brief`
with `reading_grade_target=8` enforced and `anti_patterns` strict mode.

---

## 2. `federal_councillor_v1` — type: human_panel, min_score: 0.85

**Prompt** (DE): *"Fünf Minuten vor dem Mikrofon, nur dieses Paket gelesen —
könnten Sie (a) den Composite und sein Intervall nennen, (b) die drei
prioritären KPI zitieren, (c) die drei wahrscheinlichsten Fragen ohne Zögern
beantworten?"*

**Rubric** (4 criteria, total weight 5.0): see `package_spec.json`.

### PASS sample

Three panellists (former federal communications staff) each rate:

> *composite_recall (w=1.5): 1, 1, 1 — all panellists hit composite +- 1 within 5 s.*
> *three_kpis (w=1.0): 1, 1, 0.5 — one panellist named only 2 of 3.*
> *anticipated_questions (w=1.5): 1, 1, 1 — all panellists answered fluently.*
> *no_overclaim (w=1.0): 1, 1, 1.*

Weighted median: `(1.5 + 0.5·1.0 + 1.5 + 1.0) / 5.0 = 0.90`. **Ships.**

### FAIL sample

> *composite_recall (w=1.5): 1, 1, 0 — third panellist could not locate the composite on page 1.*
> *three_kpis (w=1.0): 0.5, 0.5, 0 — KPIs were buried below the trajectory chart.*
> *anticipated_questions (w=1.5): 0.5, 0.5, 0.5 — Q&A pack was on page 2 of the bundle and not flagged in the hero card.*
> *no_overclaim (w=1.0): 1, 1, 1.*

Weighted median: `(0 + 0.5 + 0.5·1.5 + 1.0) / 5.0 = 0.45`. **Blocks.**

**Remediation:** `hero_a4_card` template promotes composite + KPIs above the
trajectory chart and adds a "→ Q&A page 2" pointer. The aim-test re-runs.

---

## 3. `policy_advisor_v1` — type: human_panel, min_score: 0.85

**Prompt** (DE): *"Kannst du allein mit diesem Paket (a) die Ministerin in 10
Minuten briefen, (b) die fünf härtesten Fragen beantworten, (c) drei
actionable Hebel mit zuständigem Akteur und Horizont auflisten?"*

### PASS sample

Panellist (a former federal department adviser) walks through the brief
verbally, hits composite, three KPIs, legal position, top risks within the
10-minute budget; cites Art. 112 LAVS and OECD WP47/2025 on demand;
identifies three levers (Conseil fédéral / 6 mois, OFAS / 12 mois, Cantons /
24 mois). **Ships.**

### FAIL sample

Panellist takes 14 minutes to brief because lever-actor-horizon matrix is
buried in a CSV without an in-brief summary. `minister_briefing_completeness`
scores 0.5; `three_actionable_levers` scores 1.0; weighted total 0.74.
**Blocks.** Remediation: the parliamentary brief renderer must inline a
3-row LAH summary on page 4.

---

## 4. `media_v1` — type: hybrid, min_score: 0.85

**Prompt** (DE): *"Kannst du mit diesem Paket allein (a) eine Meldung in 30
Minuten schreiben, (b) drei verifizierte Zitate einbauen, (c) eine
rechtefreie Illustration beifügen und korrekt zuschreiben?"*

### PASS sample

LLM judge simulates a wire reporter:

> *Lede extracted verbatim from press release H1 + lead paragraph.*
> *Three quotes pulled from quotable_lines sheet, each with claim_id.*
> *Chart `chart_pack/spider_prosper.svg` attached + alt-text in DE.*
> *Embargo card cites "Sperrfrist: 2026-04-29 06:00 CEST".*
> *Contact card lists email, phone, 09:00-18:00 window.*

Weighted score: `0.95`. **Ships.**

### FAIL sample

> *Three quotes pulled, but two of them paraphrased the original claim instead
> of citing it verbatim — `three_quotes_traceable` scores 0.3.*
> *Chart attached without alt-text in target language — `chart_publication_ready`
> scores 0.5.*

Weighted score: `0.72`. **Blocks.** Remediation: `quotable_lines` renderer
must emit verbatim strings (not paraphrases); `chart_pack` renderer must
fail-loud if alt-text is missing in any of the package's
`available_languages`.

---

## 5. `entrepreneur_v1` — type: llm_judge, min_score: 0.80

**Prompt** (DE): *"Kannst du mit diesem Paket allein (a) eine VR-Sitzung in
5 Minuten eröffnen, (b) eine CHF-Expositionsgrösse mit Intervall ankündigen,
(c) drei priorisierte Mitigationshebel vorschlagen?"*

### PASS sample

Judge:

> *Risk memo opens with "Exposition CHF 4.2M [intervalle 2.8M-6.1M], horizon T+18 mois".*
> *NOGA codes 64.19 + 65.12 named explicitly.*
> *Three levers: (1) hedging FX 3M / cost 80k / 30 j; (2) renégociation contrats clients
> 12M / cost 200k / 90 j; (3) revue gouvernance 6M / cost 50k / 60 j.*
> *Excel calculator runs with three named inputs (effectif, marge, CHF/employé).*

Weighted score: `0.88`. **Ships.**

### FAIL sample

> *Memo opens with "L'exposition pourrait être significative" — no figure, no interval.*
> *`chf_exposure_quantified` (weight 1.5) scores 0.*

Weighted score: `0.55`. **Blocks.** Remediation: `risk_memo` prompt enforces
"first sentence MUST contain a CHF figure with interval and horizon" and the
deterministic gate `no_inference_beyond_evidence` rejects hedge-words in the
opening sentence.

---

## 6. `interest_group_v1` — type: hybrid, min_score: 0.80

**Prompt** (DE): *"Kannst du mit diesem Paket allein (a) die Verbandsposition
vor Journalistinnen verteidigen, (b) innerhalb einer Stunde einen
Mitglieder-Newsletter versenden, (c) die Konstituenzwirkung in CHF pro
Segment beziffern?"*

### PASS sample

Judge + one human reviewer (from the federation comms team):

> *Federation quote: "Pour nos 4'200 membres, l'impact moyen est de CHF 18'000/an
> [intervalle 12'000-26'000] sur l'horizon T+5." Traces to claim_id 0142.*
> *Newsletter has subject + header + 4 sections + CTA + footer; renders in
> Mailchimp without manual edits.*
> *Constituency note breaks down impact across 5 segments (PME, indépendants,
> grands employeurs, sous-traitants, retraités) each with central + interval.*
> *Advocacy disclosure footer: "Analyse PTT au service de [federation_id]."*

Weighted score: `0.91`. **Ships.**

### FAIL sample

> *Federation quote names a competitor federation negatively — `no_ad_hominem`
> scores 0.*
> *Advocacy disclosure missing — `advocacy_flagged` (weight 1.5) scores 0.*

Weighted score: `0.50`. **Blocks.** Remediation: the `federation_quote`
renderer enforces (i) only THIS federation's name appears (ii) advocacy
footer is mandatory and rendered in all package channels. The deterministic
gate `no_inference_beyond_evidence` rejects any quote not pointing to a
claim_id.

---

## Notes on rubric design

- **Weights between 0.5 and 3.0.** Anything outside this band is a smell —
  if a criterion is 5× more important than another, you have two rubrics, not
  one.
- **`pass_signal_i18n` must be observable.** "Reader feels informed" is not
  observable. "Reader cites the figure and the unit" is.
- **3-8 criteria.** Fewer than 3 and the rubric can't differentiate;
  more than 8 and human reviewers diverge.
- **`min_score` calibration.** Citizen-grade `0.80`, executive-grade `0.85+`.
  Don't go to `0.95` unless you want to ship nothing.
