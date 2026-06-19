# Validation Fixtures

Use fixtures only to regression-test generic behavior. Never derive a new case's stages, entities, relationships, stage count, coordinates, or citations from a fixture.

## Complex Regression Fixture

The repository fixture at `demos/stagewise-relationship-chart/` exercises:

- dense repeated and reciprocal arrows;
- essential numeric terms;
- entity subgroup containment;
- litigation action followed by status;
- stage-specific entity and relationship citations;
- exact-quote source highlighting;
- slider navigation, dragging, marquee selection, grouped movement, persistence, and reset behavior.

Use its JSON with the skill renderer to confirm the generic renderer remains compatible:

```bash
python3 skills/legal-stagewise-relationship-chart/scripts/render_stagewise_chart.py \
  demos/stagewise-relationship-chart/stagewise_relationship_chart.json \
  /tmp/stagewise-regression.html \
  --validate-only
```

Do not mention or load this fixture during new-case legal modeling unless performing regression testing.
