# Citation Grounding

## Source Of Truth

Treat the opinion or supplied source document as the citation source of truth. Existing extraction artifacts may locate relevant passages, but verify every visible claim against the source.

Store citation text explicitly in chart JSON. The renderer must never choose or infer quote text.

## Required Source Reference

Every visible relationship and every stage-specific visible entity/container role must have at least one `source_ref` containing:

- `document_id`
- `physical_page`: one-based PDF page used internally for extraction and PDF navigation
- `printed_page`: page number printed in the opinion and shown to users
- `label`: normally `Op. p. {printed_page}`
- `quote`: exact supporting text from `physical_page`
- optional `section_or_locator`
- required `inference_note` when the displayed status is inferred rather than directly stated

Use quotes that directly support the displayed label or role. Do not cite a merely adjacent passage.

## Printed Pages

Determine printed-page offset from a reliable sequence:

1. Inspect the first several physical PDF pages.
2. Identify at least two consecutive pages whose printed page numbers also increase consecutively.
3. Calculate `offset = physical_page - printed_page`.
4. Use physical pages internally and printed pages in user-facing UI.

Do not assume the first extracted token is a printed page number.

## Inferred Status

Use an inference only when the source supports the premises and the inference is necessary to show relationship status. Add an `inference_note` explaining the reasoning without overstating the source.

## Validation

- Normalize whitespace only when matching quotes to extracted text.
- Require every quote to appear on its referenced physical page.
- Require `printed_page = physical_page - offset` for mapped opinion-body pages.
- Hide physical/extracted page numbers from the chart UI.
