---
name: legal-stagewise-relationship-chart
description: Analyze judicial opinions, legal memoranda, case PDFs, or existing legal extraction artifacts to plan, model, validate, and render interactive stage-wise relationship charts showing how legal, economic, ownership, control, contractual, and litigation relationships change through alternating status and action stages. Use for proposal-only chart modeling or complete grounded JSON plus standalone D3/HTML chart generation.
---

# Legal Stage-Wise Relationship Chart

Build a relationship-status chart whose slider reveals how relationships emerge and change over time. Treat the opinion text as the citation source of truth.

## Resources

- Read `references/modeling-rules.md` before proposing or generating stages.
- Read `references/stagewise-chart-schema.jsonc` before writing chart JSON.
- Read `references/citation-grounding.md` before creating source references or printed-page mappings.
- Read `references/validation-fixtures.md` only when regression-testing the renderer.
- Use `scripts/render_stagewise_chart.py` with `assets/template.html` to validate and render chart JSON.

## Workflow

1. **Assess chart fitness**
   - Confirm the source contains meaningful changes in relationships among parties or relevant third parties.
   - Do not force this chart onto a source containing only legal reasoning with no evolving relationship status.
   - Use existing extraction artifacts as indexes when available, but verify visible chart content against the opinion.

2. **Propose the model**
   - Identify entities, proposed stages, status-changing actions, important numbers, and material ambiguities.
   - Determine the stage count from the case facts. Never default to a fixed number of stages or copy the stage count from examples, prior charts, or regression fixtures.
   - Explain the proposed stage sequence before rendering when the user requests a plan or when the legal model is unclear.
   - Ask only about material uncertainties that cannot be resolved from the source. Do not invent relationships, directions, amounts, dates, or effects.

3. **Create grounded JSON**
   - Apply the status/action grammar and continuity rules in `references/modeling-rules.md`.
   - Follow `references/stagewise-chart-schema.jsonc`.
   - Add exact source quotes for every visible relationship and stage-specific entity role.
   - Use normalized node positions from `0` to `1`; keep continuing status-stage entities in stable positions where practical.

4. **Validate and render**

```bash
python3 skills/legal-stagewise-relationship-chart/scripts/render_stagewise_chart.py \
  path/to/stagewise_relationship_chart.json \
  path/to/stagewise-relationship-chart.html \
  --template skills/legal-stagewise-relationship-chart/assets/template.html
```

Validate without rendering:

```bash
python3 skills/legal-stagewise-relationship-chart/scripts/render_stagewise_chart.py \
  path/to/stagewise_relationship_chart.json \
  --validate-only
```

5. **Browser-QA through localhost**
   - Keep the output HTML standalone and file-openable.
   - For automated browser QA, serve the output directory through a temporary localhost server because browser automation may block `file://` navigation.
   - Inspect dense stages, reciprocal arrows, citations, containers, slider behavior, dragging, marquee selection, group movement, persistence, and reset behavior.

## Required Output Behavior

- Begin and end with a status stage; strictly alternate status and action.
- Use the minimum sufficient source-driven stage count; there is no fixed number of stages.
- Exclude courts as entity nodes.
- Make every status panel independently readable.
- Preserve continuing entities, including through explicit split, merge, replacement, containment, or removal representations.
- Show essential numeric terms in labels when readable and complete terms in tooltips.
- Use distinct lanes for repeated and reciprocal relationships.
- Render every directional relationship with an arrowhead that stops at the target entity border, including relationships with case-specific categories.
- Highlight only exact quote text stored in JSON; never guess citation text during rendering.
- Display printed opinion pages to users and keep physical PDF pages internal.

Return the chart JSON and rendered HTML paths, summarize validation results, and identify any unresolved legal-modeling uncertainties.
