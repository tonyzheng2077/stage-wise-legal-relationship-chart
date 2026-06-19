# Stage-Wise Legal Relationship Chart

This repository contains a Codex skill for creating interactive legal relationship charts from judicial opinions, legal memoranda, and case PDFs.

The chart is designed for lawyers who need to understand how the legal, economic, contractual, ownership, control, or litigation relationships among parties changed over time.

## What The Skill Creates

The skill creates a standalone HTML chart with two connected parts:

- an upper relationship chart showing parties, relevant third parties, and their relationships;
- a lower stage axis with a slider that moves through the relationship history.

Each stage is either:

- **Status**: the relationship state at a particular point in time; or
- **Action**: an act between parties that changes the relationship state.

The chart strictly alternates:

```text
status -> action -> status -> action -> status
```

There is no fixed number of stages. The stage count is determined from the case facts.

## Why This Is Useful

Many legal disputes turn on relationship changes, not just chronology. Examples include:

- a merger agreement is signed, disputed, terminated, and litigated;
- a company restructures ownership or control rights;
- a financing or stock issuance changes economic rights;
- one party sues another, producing a new legal status;
- a contractual condition fails and changes closing obligations.

This chart helps readers see those changes as a sequence of relationship states, instead of reading them only as a timeline.

## Lawyer-Readable Modeling Rules

The skill is opinion-grounded and relationship-focused.

It instructs the agent to:

- exclude courts and judges as entity nodes;
- include only dispute parties and relevant third parties;
- treat court rulings as status effects or annotations, not as actors;
- show all continuing entities in later status stages unless the source supports a split, merger, replacement, or removal;
- show action stages only when an entity action changes relationship status;
- treat outside events, such as market decline or financing pressure, as background context rather than action stages;
- treat lawsuits between parties as action stages, followed by a resulting status stage;
- make every status chart readable on its own, without labels like "still owns."

## Citations And Source Grounding

Every visible relationship and every visible entity role must be supported by exact quoted text from the source document.

The generated chart includes citation buttons. Clicking a citation opens a source panel with:

- the printed opinion page number;
- the exact quote used to support the chart item;
- highlighted source text extracted from the PDF;
- an option to open the original PDF page.

The renderer does not guess citation text. Citation quotes must be stored directly in the chart JSON.

## Visual Behavior

The HTML renderer supports:

- solid frames for status stages;
- dotted frames for action stages;
- greyed prior stages and emphasized active stage;
- arrows that stop at entity borders;
- separated lanes for reciprocal or repeated relationships;
- wrapped edge labels;
- draggable nodes and labels;
- marquee selection and group movement;
- persistent layout overrides in browser local storage;
- reset controls.

## Repository Contents

- `SKILL.md`: main Codex skill instructions.
- `scripts/render_stagewise_chart.py`: validates chart JSON and renders standalone HTML.
- `assets/template.html`: D3-based interactive chart template.
- `references/modeling-rules.md`: legal modeling rules.
- `references/citation-grounding.md`: citation and printed-page rules.
- `references/stagewise-chart-schema.jsonc`: generic chart JSON interface.
- `references/validation-fixtures.md`: guidance for regression testing.
- `agents/openai.yaml`: skill metadata.

## Basic Use

Ask Codex to use the skill on a case opinion or legal memo:

```text
Use the legal-stagewise-relationship-chart skill to create a stage-wise relationship chart for this opinion.
```

The expected output is:

- a chart JSON file;
- a standalone HTML file;
- validation notes describing stage choices and unresolved uncertainties.

The HTML file can be opened directly in a browser.

## Validation

The renderer checks:

- strict status/action alternation;
- final stage is a status;
- no court entities;
- valid entity and relationship references;
- continuity across status stages;
- exact quote matching against extracted PDF text;
- printed-page mapping;
- visible entity citations;
- distinct lanes for repeated or reciprocal edges.

## Intended Audience

This skill is built for lawyers, legal researchers, litigation teams, transactional lawyers, and legal-technology teams who want to convert dense case facts into an interactive relationship-status visualization.
