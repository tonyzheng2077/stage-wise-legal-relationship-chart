#!/usr/bin/env python3
"""Validate and render generic stage-wise relationship chart JSON into standalone HTML.

Usage:
    python3 render_stagewise_chart.py chart.json chart.html
    python3 render_stagewise_chart.py chart.json --validate-only
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def stage_ids(data: dict) -> list[str]:
    return [stage["id"] for stage in data.get("stages", [])]


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip().lower()


def extract_pdf_pages(path: Path) -> list[str]:
    try:
        from pypdf import PdfReader
    except ImportError:
        return []

    reader = PdfReader(str(path))
    return [(page.extract_text() or "").strip() for page in reader.pages]


def detect_printed_page_offset(pages: list[str]) -> int | None:
    """Find a reliable early sequence where physical pages map to printed pages."""
    candidates: list[tuple[int, int]] = []
    for physical_index, text in enumerate(pages[:15], start=1):
        match = re.match(r"^\s*(\d{1,3})\b", text or "")
        if match:
            candidates.append((physical_index, int(match.group(1))))
    for (physical_a, printed_a), (physical_b, printed_b) in zip(candidates, candidates[1:]):
        if physical_b == physical_a + 1 and printed_b == printed_a + 1:
            return physical_a - printed_a
    return None


def attach_source_pages(data: dict, input_path: Path | None = None) -> dict:
    data = json.loads(json.dumps(data))
    source_pages: dict[str, dict[str, str]] = {}
    base_dir = input_path.parent if input_path else Path.cwd()
    for document in data.get("documents", []):
        document_id = document.get("id")
        raw_path = document.get("source_path") or document.get("path") or ""
        if not document_id or not raw_path:
            continue
        pdf_path = Path(raw_path)
        if not pdf_path.is_absolute():
            pdf_path = (base_dir / pdf_path).resolve()
            if not pdf_path.exists() and document.get("filename"):
                pdf_path = (base_dir / document["filename"]).resolve()
        if not pdf_path.exists():
            continue
        pages = extract_pdf_pages(pdf_path)
        if pages:
            source_pages[document_id] = {str(index): text for index, text in enumerate(pages, start=1)}
            offset = detect_printed_page_offset(pages)
            if offset is not None:
                document["printed_page_offset"] = offset
    if source_pages:
        data["source_pages"] = source_pages
    return data


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    stages = data.get("stages", [])
    ids = stage_ids(data)
    entities = {entity.get("id"): entity for entity in data.get("entities", [])}
    documents = {document.get("id"): document for document in data.get("documents", [])}
    nodes_by_stage = data.get("nodes_by_stage", {})
    containers_by_stage = data.get("containers_by_stage", {})
    relationships_by_stage = data.get("relationships_by_stage", {})
    entity_refs_by_stage = data.get("entity_refs_by_stage", {})
    continuity_rules = data.get("continuity_rules", {})
    continuity_transitions = continuity_rules.get("transitions", [])
    source_pages = data.get("source_pages", {})

    def validate_source_refs(stage_id: str, item_id: str, refs: list[dict], required: bool = True) -> None:
        if required and not refs:
            errors.append(f"{stage_id}.{item_id} must include at least one source_ref.")
        for ref in refs:
            document_id = ref.get("document_id")
            physical_page = ref.get("physical_page")
            printed_page = ref.get("printed_page")
            if document_id not in documents:
                errors.append(f"{stage_id}.{item_id} source_refs document_id unknown: {document_id}.")
            if "page" in ref:
                errors.append(f"{stage_id}.{item_id} source_ref must use physical_page/printed_page, not page.")
            if not isinstance(physical_page, int) or physical_page < 1:
                errors.append(f"{stage_id}.{item_id} physical_page must be a positive integer: {physical_page}.")
            if not isinstance(printed_page, int) or printed_page < 1:
                errors.append(f"{stage_id}.{item_id} printed_page must be a positive integer: {printed_page}.")
            document = documents.get(document_id, {})
            offset = document.get("printed_page_offset")
            if isinstance(offset, int) and isinstance(physical_page, int) and physical_page > offset:
                expected_printed = physical_page - offset
                if printed_page != expected_printed:
                    errors.append(
                        f"{stage_id}.{item_id} printed_page must equal physical_page - {offset}: "
                        f"expected {expected_printed}, got {printed_page}."
                    )
            quote = ref.get("quote")
            if not isinstance(quote, str) or not quote.strip():
                errors.append(f"{stage_id}.{item_id} physical page {physical_page} is missing quote text.")
            else:
                document_pages = source_pages.get(str(document_id))
                page_text = document_pages.get(str(physical_page), "") if document_pages else ""
                if document_pages and not page_text:
                    errors.append(f"{stage_id}.{item_id} physical page not found in extracted source: {physical_page}.")
                elif page_text and normalize_text(quote) not in normalize_text(page_text):
                    errors.append(f"{stage_id}.{item_id} quote not found on physical page {physical_page}.")

    def represented_entity_ids(stage_id: str) -> set[str]:
        represented = {node.get("entity_id") for node in nodes_by_stage.get(stage_id, [])}
        represented.update(container.get("entity_id") for container in containers_by_stage.get(stage_id, []))
        return {entity_id for entity_id in represented if entity_id}

    def transition_changes(from_stage_id: str, to_stage_id: str) -> list[dict]:
        changes: list[dict] = []
        for transition in continuity_transitions:
            if transition.get("from_stage_id") == from_stage_id and transition.get("to_stage_id") == to_stage_id:
                changes.extend(transition.get("changes", []))
        return changes

    def is_number(value: object) -> bool:
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    def relationship_pair_key(rel: dict) -> str:
        return str(rel.get("lane_group") or "::".join(sorted([str(rel.get("source")), str(rel.get("target"))])))

    def effective_lane_values(group: list[dict]) -> list[tuple[str, float]]:
        explicit_slots = all(is_number(rel.get("lane_slot")) for rel in group)
        default_step = 0.24 if len(group) >= 4 else 0.3
        step = max(float(group[0].get("lane_step") or default_step), 0.18)
        if explicit_slots:
            return [(str(rel.get("id")), float(rel.get("lane_slot")) * step) for rel in group]
        sorted_group = sorted(group, key=lambda rel: (float(rel.get("curve") or 0), str(rel.get("source")), str(rel.get("id"))))
        return [(str(rel.get("id")), (index - (len(sorted_group) - 1) / 2) * step) for index, rel in enumerate(sorted_group)]

    if data.get("chart_type") != "stagewise_relationship_chart":
        errors.append("chart_type must be 'stagewise_relationship_chart'.")
    if not stages:
        errors.append("stages must be non-empty.")

    allowed_change_kinds = {"removal", "replacement", "split", "merge"}
    for transition_index, transition in enumerate(continuity_transitions):
        from_stage_id = transition.get("from_stage_id")
        to_stage_id = transition.get("to_stage_id")
        transition_label = f"continuity transition {transition_index + 1}"
        if from_stage_id not in ids or to_stage_id not in ids:
            errors.append(f"{transition_label} references an unknown stage.")
            continue
        from_entities = represented_entity_ids(from_stage_id)
        to_entities = represented_entity_ids(to_stage_id)
        for change_index, change in enumerate(transition.get("changes", [])):
            change_label = f"{transition_label}.change {change_index + 1}"
            kind = change.get("kind")
            source_ids = change.get("from_entity_ids", [])
            target_ids = change.get("to_entity_ids", [])
            if kind not in allowed_change_kinds:
                errors.append(f"{change_label} has invalid kind: {kind}.")
            if not isinstance(source_ids, list) or not source_ids:
                errors.append(f"{change_label} must include from_entity_ids.")
                source_ids = []
            if kind == "removal" and target_ids:
                errors.append(f"{change_label} removal must not include to_entity_ids.")
            if kind != "removal" and (not isinstance(target_ids, list) or not target_ids):
                errors.append(f"{change_label} {kind} must include to_entity_ids.")
                target_ids = []
            for entity_id in source_ids:
                if entity_id not in entities:
                    errors.append(f"{change_label} references unknown source entity {entity_id}.")
                elif entity_id not in from_entities:
                    errors.append(f"{change_label} source entity not represented in {from_stage_id}: {entity_id}.")
            for entity_id in target_ids:
                if entity_id not in entities:
                    errors.append(f"{change_label} references unknown target entity {entity_id}.")
                elif entity_id not in to_entities:
                    errors.append(f"{change_label} target entity not represented in {to_stage_id}: {entity_id}.")
            if not str(change.get("reason") or "").strip():
                errors.append(f"{change_label} must include a reason.")
            validate_source_refs(to_stage_id, f"continuity:{change_index + 1}", change.get("source_refs", []))

    for forbidden in ("court", "chancery", "judge", "tribunal"):
        for entity in data.get("entities", []):
            text = f"{entity.get('id', '')} {entity.get('label', '')} {entity.get('type', '')}".lower()
            if forbidden in text:
                errors.append(f"Forbidden court-related entity found: {entity.get('id')}")

    expected = "status"
    for idx, stage in enumerate(stages):
        actual = stage.get("type")
        if actual != expected:
            errors.append(f"Stage {stage.get('id')} must be {expected}, got {actual}.")
        if idx < len(stages) - 1:
            expected = "action" if actual == "status" else "status"
    if stages and stages[-1].get("type") != "status":
        errors.append("Final stage must be a status stage.")

    for stage_id in ids:
        nodes = nodes_by_stage.get(stage_id)
        if not nodes:
            errors.append(f"{stage_id} has no nodes_by_stage entries.")
            continue
        stage_node_ids = {node.get("entity_id") for node in nodes}
        for node in nodes:
            entity_id = node.get("entity_id")
            if entity_id not in entities:
                errors.append(f"{stage_id} references unknown entity {entity_id}.")
            for coord in ("x", "y"):
                value = node.get(coord)
                if not is_number(value) or not 0 <= value <= 1:
                    errors.append(f"{stage_id}.{entity_id} has invalid {coord}: {value}.")
        for container in containers_by_stage.get(stage_id, []):
            entity_id = container.get("entity_id")
            contained = container.get("contains", [])
            if entity_id not in entities:
                errors.append(f"{stage_id} container references unknown entity {entity_id}.")
            if not isinstance(contained, list) or not contained:
                errors.append(f"{stage_id}.{entity_id} container must include contained entity ids.")
            for child_id in contained:
                if child_id not in stage_node_ids:
                    errors.append(f"{stage_id}.{entity_id} container child not visible: {child_id}.")
        relationships = relationships_by_stage.get(stage_id, [])
        for rel in relationships:
            if rel.get("source") not in stage_node_ids:
                errors.append(f"{stage_id}.{rel.get('id')} source not visible: {rel.get('source')}.")
            if rel.get("target") not in stage_node_ids:
                errors.append(f"{stage_id}.{rel.get('id')} target not visible: {rel.get('target')}.")
            if "still" in str(rel.get("label", "")).lower().split():
                errors.append(f"{stage_id}.{rel.get('id')} label must not use 'still'.")
            validate_source_refs(stage_id, str(rel.get("id") or "relationship"), rel.get("source_refs", []))
            if rel.get("inferred"):
                for ref in rel.get("source_refs", []):
                    if not str(ref.get("inference_note") or "").strip():
                        errors.append(f"{stage_id}.{rel.get('id')} inferred relationship requires inference_note.")
        lane_groups: dict[str, list[dict]] = {}
        for rel in relationships:
            lane_groups.setdefault(relationship_pair_key(rel), []).append(rel)
        for group_key, group in lane_groups.items():
            if len(group) < 2:
                continue
            lanes = effective_lane_values(group)
            rounded = [round(value, 4) for _, value in lanes]
            if len(set(rounded)) != len(rounded):
                errors.append(f"{stage_id}.{group_key} has overlapping edge lanes: {lanes}.")
            sorted_lanes = sorted(lanes, key=lambda item: item[1])
            for (left_id, left_lane), (right_id, right_lane) in zip(sorted_lanes, sorted_lanes[1:]):
                if abs(right_lane - left_lane) < 0.18:
                    errors.append(
                        f"{stage_id}.{group_key} edge lanes are too close: "
                        f"{left_id}={left_lane:.3f}, {right_id}={right_lane:.3f}."
                    )
        for entity_id in represented_entity_ids(stage_id):
            entity_ref = entity_refs_by_stage.get(stage_id, {}).get(entity_id, {})
            validate_source_refs(stage_id, f"entity:{entity_id}", entity_ref.get("source_refs", []))

    for stage in stages:
        if stage.get("type") != "status" or not stage.get("carry_forward_from"):
            continue
        stage_id = stage["id"]
        prior_id = stage["carry_forward_from"]
        if prior_id not in nodes_by_stage:
            errors.append(f"{stage_id} carry_forward_from unknown stage {prior_id}.")
            continue
        changes = transition_changes(prior_id, stage_id)
        explained_missing = {
            entity_id
            for change in changes
            for entity_id in change.get("from_entity_ids", [])
        }
        missing = sorted(represented_entity_ids(prior_id) - represented_entity_ids(stage_id) - explained_missing)
        if missing:
            errors.append(f"{stage_id} fails continuity from {prior_id}: missing {', '.join(missing)}.")

    return errors


def render(data: dict, template_path: Path) -> str:
    template = template_path.read_text(encoding="utf-8")
    payload = json.dumps(data, indent=2, ensure_ascii=False)
    title = html.escape(data.get("chart_title", "Stage-Wise Relationship Chart"))
    return template.replace("__CHART_TITLE__", title).replace("/* __STAGEWISE_DATA__ */", payload)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path, nargs="?")
    parser.add_argument("--template", type=Path, default=Path(__file__).parents[1] / "assets" / "template.html")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    data = attach_source_pages(load_json(args.input), args.input)
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Validated {len(data['stages'])} stages and {len(data['entities'])} entities.")

    if args.validate_only:
        return 0
    if args.output is None:
        print("ERROR: output path is required unless --validate-only is used.", file=sys.stderr)
        return 2

    args.output.write_text(render(data, args.template), encoding="utf-8")
    print(f"Rendered {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
