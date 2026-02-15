from __future__ import annotations

import csv
import os
import re
from pathlib import Path
from typing import Any

import yaml
from googleapiclient.discovery import build
from google.auth import default

ROOT = Path(__file__).resolve().parents[1]  # repo root
VIRTUES_DIR = ROOT / "virtues"
VICES_DIR = ROOT / "vices"
RELATIONS_DIR = ROOT / "relations"

SPREADSHEET_ID = os.environ["SPREADSHEET_ID"]

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def read_front_matter(md_path: Path) -> dict[str, Any] | None:
    """Return YAML front matter dict or None if missing/invalid."""
    text = md_path.read_text(encoding="utf-8", errors="replace")
    m = FM_RE.match(text)
    if not m:
        return None
    try:
        data = yaml.safe_load(m.group(1))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def normalize_tags(tags: Any) -> str:
    if isinstance(tags, list):
        return ", ".join(str(t) for t in tags)
    if isinstance(tags, str):
        return tags
    return ""


def normalize_refs(refs: Any) -> str:
    """
    Store refs as a simple string for now:
    - if list of dicts: "CCC: 1814; ST: II-II q.1–7"
    - if dict: "CCC: 1814; ST: ..."
    - else: ""
    """
    parts: list[str] = []
    if isinstance(refs, list):
        for item in refs:
            if isinstance(item, dict):
                for k, v in item.items():
                    parts.append(f"{k}: {v}")
    elif isinstance(refs, dict):
        for k, v in refs.items():
            parts.append(f"{k}: {v}")
    return "; ".join(parts)


def build_elements() -> list[list[str]]:
    header = ["Label", "id", "type", "family", "tags", "refs", "path"]
    rows: list[list[str]] = [header]

    for base in (VIRTUES_DIR, VICES_DIR):
        if not base.exists():
            continue
        for md in sorted(base.rglob("*.md")):
            fm = read_front_matter(md)
            if not fm:
                continue  # skip files without YAML front matter

            _id = str(fm.get("id", "")).strip()
            label = str(fm.get("label", _id)).strip()
            typ = str(fm.get("type", fm.get("kind", ""))).strip()
            family = str(fm.get("family", "")).strip()
            tags = normalize_tags(fm.get("tags"))
            refs = normalize_refs(fm.get("refs"))

            if not _id:
                continue  # id is required

            rel_path = md.relative_to(ROOT).as_posix()
            rows.append([label, _id, typ, family, tags, refs, rel_path])

    return rows


def build_connections() -> list[list[str]]:
    # We canonicalize columns for Kumu/Sheets:
    # from, to, type, weight, ref, note
    header = ["From", "To", "type", "weight", "ref", "note"]

    rows: list[list[str]] = [header]

    if not RELATIONS_DIR.exists():
        return rows

    for csv_path in sorted(RELATIONS_DIR.glob("*.csv")):
        rel_type = csv_path.stem  # Option 1: filename defines relation type

        # Skip empty files (or files with only header)
        text = csv_path.read_text(encoding="utf-8", errors="replace").strip()
        if not text:
            continue

        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                continue

            found_data = False
            for r in reader:
                # skip completely blank rows
                if not any((v or "").strip() for v in r.values()):
                    continue

                found_data = True
                src = (r.get("from") or "").strip()
                dst = (r.get("to") or "").strip()
                weight = (r.get("weight") or "").strip()
                ref = (r.get("ref") or "").strip()
                note = (r.get("note") or "").strip()

                # require from/to at minimum
                if not src or not dst:
                    continue

                rows.append([src, dst, rel_type, weight, ref, note])

            if not found_data:
                continue

    return rows


def clear_and_write(spreadsheets_resource, tab: str, values: list[list[str]]) -> None:
    # Clear tab first (so old rows don’t linger)
    spreadsheets_resource.values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{tab}!A:Z",
        body={},
    ).execute()

    # Write new values
    spreadsheets_resource.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{tab}!A1",
        valueInputOption="RAW",
        body={"values": values},
    ).execute()


def main() -> None:
    creds, _ = default(scopes=["https://www.googleapis.com/auth/spreadsheets"])
    service = build("sheets", "v4", credentials=creds)
    spreadsheets = service.spreadsheets()

    elements = build_elements()
    connections = build_connections()

    clear_and_write(spreadsheets, "elements", elements)
    clear_and_write(spreadsheets, "connections", connections)


if __name__ == "__main__":
    main()

