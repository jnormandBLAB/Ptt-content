# Adapter Refactor — From Cell Matrix to Package Dispatch

## Today (to be replaced)

`src/ptt_stakeholder_adapter/stakeholder_matrix.py` defines a 24-cell matrix
keyed by `f"{output_type}_{audience}"` (e.g. `brief_citizen`,
`fact_card_policy`, `infographic_media`). `run.py` iterates the cartesian
product `[audience x output_type]`, looks up each cell, calls a renderer per
cell. Audience profiles live in `AUDIENCE_PROFILES`. Quality is measured by
the nine deterministic gates in `quality_gate.py`.

This couples three things that should not be coupled: **who** the package is
for, **what** is in the package, and **how** it is rendered. The result is
24 cookie-cutter cells that all look like cousins of each other.

## Tomorrow (target)

The adapter loads a list of `package_spec.json` files (from
`packages/*/package_spec.json`), and for each spec it iterates the
`artefacts[]` array. For each artefact it dispatches to the renderer
identified by `artefact.renderer` against a renderer registry. The registry
is the only place renderer ids resolve to Python callables.

```python
# proposed src/ptt_stakeholder_adapter/run.py (sketch)

from ptt_stakeholder_adapter.package_loader import load_package_specs
from ptt_stakeholder_adapter.renderers.registry import get_renderer
from ptt_stakeholder_adapter.aim_test import run_aim_test
from ptt_stakeholder_adapter.quality_gate import run_deterministic_gates

def run(report, package_ids: list[str], languages: list[str]) -> AdapterRun:
    specs = load_package_specs(package_ids)            # validates each against schema
    out = AdapterRun()
    for spec in specs:
        for lang in spec.stakeholder.available_languages:
            if lang not in languages:
                continue
            for artefact in spec.artefacts:
                renderer = get_renderer(artefact.renderer)   # registry lookup
                result   = renderer.render(report, artefact, spec, lang)
                gates    = run_deterministic_gates(result, artefact)
                if gates.failed:
                    out.add_failure(spec, artefact, gates); continue
                emit_provenance("ADAPTER_RENDERED", spec, artefact, result)
                out.add_success(spec, artefact, result)
            aim    = run_aim_test(spec, lang, out.results_for(spec, lang))
            if aim.score < spec.aim_test.min_score:
                out.flag_for_regen(spec, lang, aim)
                emit_provenance("ADAPTER_QA", spec, lang, aim)
    return out
```

## Renderer registry

Replace the per-cell renderer modules (`renderers/brief.py`,
`renderers/fact_card.py`, ...) with a registry that resolves logical ids
(`brief.executive_a4_v1`, `chart.trajectory_v1`, `audio.tts_swiss_voices_v1`)
to renderer classes. Each renderer accepts `(report, artefact_spec,
package_spec, language)` and returns a `RenderedArtefact` with
`{file_paths_per_channel, claim_ids, evidence_ids, narrative_ids,
schema_org_jsonld, provenance_sidecar}`. This is the only hot path that
needs to change shape.

```
src/ptt_stakeholder_adapter/renderers/
  registry.py           # id -> renderer class (entry-point discoverable)
  base.py               # RendererProtocol, RenderedArtefact
  brief/                # brief.civic_v1, brief.executive_a4_v1, ...
  chart/                # chart.trajectory_v1, chart.press_pack_v1, ...
  audio/                # audio.tts_swiss_voices_v1
  table/                # table.lah_matrix_v1, table.noga_exposure_v1
  press/                # press.release_v1, press.quotables_v1
  email/                # email.newsletter_v1
  social/               # social.share_pack_v1
  spreadsheet/          # spreadsheet.cost_calculator_v1
```

## Files to delete after migration

- `stakeholder_matrix.py` — replaced by package_spec discovery.
- The audience-x-output cells in `prompts/` survive but are renamed and
  organised by renderer id, not by cell key.
- `bless_drift.py` and `nudge_engine.py` move into the relevant renderer
  packages — they become tactics inside a renderer, not cross-cutting concerns.

## Files to add

- `package_loader.py` — discovers and validates `package_spec.json` against
  `packages/_schema/package_spec.schema.json`.
- `aim_test.py` — runs the rubric (LLM judge / human panel / hybrid).
- `renderers/registry.py` — single dispatch surface.

## Migration plan

1. Land the new `packages/` directory and the schema (this PR — done).
2. Add `package_loader.py` that loads + validates specs. Wire into a
   `--use-packages` opt-in flag on `run.py`. Old code path stays intact.
3. Implement the renderer registry plus 5-7 renderers covering
   `citizen_v1` end-to-end. Smoke-test on a real report.
4. Migrate the remaining 5 packages renderer-by-renderer; delete the old
   cell entries as they become orphans.
5. Flip the default to `--use-packages=true`. Mark `stakeholder_matrix.py`
   deprecated. Delete after one release of soak time.

The schema is the bridge — once it lives, the migration is incremental and
each step is independently shippable.
