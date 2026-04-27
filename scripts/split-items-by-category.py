#!/usr/bin/env python3
"""
Split `lib/items.json` into per-category files under `lib/items/`.

This is intentionally a 1:1 copy of the current item rows (no shape migration).
Output is sorted by `id` for stable diffs.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path


def slug_category(category: str) -> str:
    s = (category or "other").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"(^-|-$)", "", s)
    return s or "other"


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    lib_dir = root / "lib"
    src_path = lib_dir / "items.json"
    out_dir = lib_dir / "items"

    if not src_path.exists():
        raise SystemExit(f"Missing source file: {src_path}")

    items = json.loads(src_path.read_text(encoding="utf-8"))
    if not isinstance(items, list):
        raise SystemExit("lib/items.json: expected root array")

    out_dir.mkdir(parents=True, exist_ok=True)

    by_category: dict[str, list[dict]] = {}
    for row in items:
        category = row.get("category") if isinstance(row, dict) else None
        category = str(category) if category is not None else "Other"
        by_category.setdefault(category, []).append(row)

    outputs = []
    for category, rows in by_category.items():
        filename = f"{slug_category(category)}.json"
        outputs.append((filename, category, rows))
    outputs.sort(key=lambda t: t[0])

    for filename, category, rows in outputs:
        rows.sort(key=lambda r: str(r.get("id") if isinstance(r, dict) else ""))
        out_path = out_dir / filename
        out_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        rel = os.path.relpath(out_path, root)
        print(f"Wrote {rel} ({len(rows)}) from category {category!r}")


if __name__ == "__main__":
    main()

