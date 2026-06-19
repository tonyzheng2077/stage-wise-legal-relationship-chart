# Stage-Wise Legal Relationship Modeling Rules

## Chart Fitness

Use this chart only when a source describes meaningful changes in legal, economic, ownership, control, contractual, organizational, or litigation relationships among identifiable entities.

Do not force the chart onto a source containing only legal reasoning, issue comparison, or chronology without evolving relationship status.

## Stage Grammar

- Begin with a status stage and end with a status stage.
- Strictly alternate `status -> action -> status`.
- Do not target a fixed number of stages. Choose the minimum sufficient number of stages required by the source's relationship-changing actions and resulting statuses.
- A status stage shows the operative relationship state at that point.
- An action stage shows only acts between or among entities that change relationship status.
- An action must be followed by the resulting status.
- Combine multiple related acts into one action stage when they collectively produce one fundamental status change.
- Treat external events such as market movements, regulatory climate, or financing pressure as stage background, not action stages.
- Treat a lawsuit by one entity against another as an action. Follow materially different trial or appeal outcomes with separate status stages.
- Exclude courts, judges, and tribunals as entity nodes. Show their rulings as status effects or background.

## Entities And Continuity

- Status stages show every continuing entity that still exists.
- Action stages show only participating entities.
- Preserve stable entity IDs and positions across status stages where practical.
- When a parent entity splits into subgroups, show the parent as a dotted container around the subgroups; do not show it as a parallel duplicate node.
- Explicitly explain entity removal, replacement, merger, split, or containment.
- When continuity cannot be represented by carrying forward the same entity id or a same-id container, declare a grounded `continuity_rules.transitions[]` change. A removal has no target; a replacement, split, or merge names the resulting visible entities.
- Keep counsel, officers, employees, and agents in relationship tooltip details unless their separate existence is necessary to understand the status change.

## Relationships

- Make each status stage independently readable. Avoid relative words such as "still," "remains," or "continues" when a direct status label works.
- Draw one relationship for a containing legal/economic instrument. Put subordinate rights, duties, formulas, and consequences in its tooltip rather than drawing misleading parallel arrows.
- Put essential amounts, percentages, quantities, and ownership shares in labels when readable; put complete terms in tooltips.
- Represent contemplated or conditional relationships as conditional. Represent failed or unavailable relationships distinctly.
- Treat relationship direction as meaningful. Directional edges must render with visible arrowheads ending at the target entity border; do not rely on labels alone to communicate direction.
- Assign separate visual lanes to every repeated or reciprocal source/target relationship. Add explicit `lane_group`, `lane_slot`, and `lane_step` for dense or legally significant groups.

## Model Review

Before rendering, verify:

- Every action changes a relationship status.
- Every status change has a preceding entity action.
- No outside event is mislabeled as an action.
- No parent entity is duplicated beside its subgroups.
- No separate arrows represent terms that are merely contents of one relationship.
- Every visible node and edge is necessary for understanding the relationship state.
