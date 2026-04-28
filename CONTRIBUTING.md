# Contributing — PTT Content Repo

Bilingual quick guide (FR / EN). Le but : permettre à toute l'équipe contenu
de corriger une faute de frappe ou d'ajuster un libellé sans toucher à du
code Python. The goal: let the content team ship a typo fix or a wording
tweak in four clicks, no Python required.

---

## Comment corriger une faute de frappe en 4 clics / How to fix a typo in 4 clicks

1. **Naviguer** vers le fichier sur GitHub
   `<stakeholder>_v1/package_spec.json` (par ex.
   `citizen_v1/package_spec.json`).
2. **Cliquer sur le crayon** (Edit this file) en haut à droite.
3. **Modifier** le texte. La validation de schéma se fait automatiquement
   en CI ; vous pouvez prévisualiser le diff avant de proposer le change.
4. **Propose changes** -> ouvre une Pull Request. CODEOWNERS sera
   automatiquement assigné. Deux relecteurs sont requis sur `main`.

After merge: the dispatch workflow notifies FALC / TTS / push pipelines.
A Renovate auto-PR will bump `@ptt/content` in the main `Claude_ptt`
repo. Live citizen page reflects the change in <= 30 min.

---

## Required fields / Champs obligatoires

The full contract lives in `_schema/package_spec.schema.json`. The five
fields you will encounter most often:

1. `package_id` — string, must match the directory name
   (e.g. `citizen_v1`).
2. `stakeholder_persona` — one of the canonical persona slugs.
3. `falc_eligible` — `true` if the package contains FALC (Falc =
   Français Facile A Lire et a Comprendre / Plain language) content.
4. `every_voices_meta.falc` — block carrying FALC reviewer signoff and
   readability score (when `falc_eligible: true`).
5. `analytics.stakeholder_cohort` — must match an existing cohort label;
   ask in the PR if unsure.

---

## Language rules / Regles linguistiques

- **FR** — French (Swiss federal). Primary language.
- **DE** — Swiss German. Use `ss` instead of `ss` (eszett `s,s,`); this
  is the Swiss federal admin standard.
- **IT** — Italian (Ticino).
- **RM** — Rumantsch Grischun. Optional for some packages; if omitted,
  set the corresponding field block to `optional: true` and document why.

All four languages should be updated together when content text changes.

---

## Two-PR pattern / Le motif "deux PRs"

Each content change ships in two automatic PRs:

1. **PR A** — your edit lands here (this repo, `Ptt-content`). On merge:
   - the `dispatch-on-merge` workflow signs and POSTs to the FALC / TTS /
     push staging endpoints (analytics-grade — failures are warnings,
     not errors);
   - the `publish` workflow runs only on a `v*.*.*` tag. We tag after a
     batch of merges, not per-PR.
2. **PR B** — Renovate opens a follow-up PR in `Claude_ptt` to bump the
   pinned `@ptt/content` version. When that merges and deploys, the live
   citizen page reflects your edit. Target latency: <= 30 min end-to-end.

You only ever interact with PR A. PR B is fully automated.

---

## Schema validation cheat-sheet

CI runs `ajv` against `_schema/package_spec.schema.json`. Common errors:

| ajv error | What it means | How to fix |
|-----------|---------------|------------|
| `must have required property 'X'` | Field missing | Add the field; check schema for the exact name. |
| `must be string` / `must be boolean` | Wrong type | Quote strings; remove quotes from booleans. |
| `must match pattern "..."` | Slug shape wrong | Lowercase, snake_case, no accents in IDs. |
| `must NOT have additional properties` | Typo in field name | Delete the unknown key, or add it to the schema in a separate PR. |
| `must be equal to one of the allowed values` | Enum mismatch | Open the schema, find the enum, copy a valid value. |

Run locally before pushing (optional):

```bash
npx -p ajv-cli@5 -p ajv-formats@3 ajv validate \
  -s _schema/package_spec.schema.json \
  -d "*_v*/package_spec.json" \
  --spec=draft2020 -c ajv-formats --strict=false
```

---

## Things NOT to put in this repo

- No personal data / PII in any text field. Names of public officials in
  their public role are fine; private citizens are not.
- No secrets, API keys, tokens.
- No binaries or large media. Reference assets by URL.

When in doubt, ask in the PR.
