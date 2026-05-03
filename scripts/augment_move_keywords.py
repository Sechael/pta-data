#!/usr/bin/env python3
"""Add mechanics.move_keyword to lib/moves.json (before effects). See schemas/moveschema.json."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOVES = ROOT / "lib" / "moves.json"

RE_REACTION = re.compile(r"\bused\s+as\s+a\s+Reaction\b|\bas\s+a\s+Reaction\b", re.I)
RE_SCATTER = re.compile(r"\bScatter\s+attack\b", re.I)
RE_BINDING_MOVE = re.compile(r"\bBinding\s+Move\b|\bbinding\s+move\b", re.I)
RE_MULTITURN = re.compile(r"\btwo-turn\s+move\b|\btwo\s+turn\s+move\b", re.I)
RE_TERRAIN_CREATE = re.compile(
    r"\b(?:at\s+the\s+center\s+of\s+the\s+blast,\s*)?you\s+create\s+a\s+circle\s+of[^\n]{0,160}\bterrain\b",
    re.I,
)
RE_WEATHER_CREATE = re.compile(
    r"\b(?:at\s+the\s+center\s+of\s+the\s+blast,\s*)?you\s+create\s+a\s+circle\s+of[^\n]{0,160}\bweather\b",
    re.I,
)
RE_HAZARD_PLACE = re.compile(r"\bplace\s+(?:a|the)\s+[^\n]{0,80}\bhazard\b", re.I)
RE_COAT_PUT = re.compile(
    r"\bput\s+a\s+[^\n]{0,40}\bcoat\b|\bgains?\s+a\s+[^\n]{0,40}\bcoat\b|\bgets?\s+a\s+[^\n]{0,40}\bcoat\b|\breceive(?:s|d)?\s+[^\n]{0,20}\bcoats?\b",
    re.I,
)
RE_PRIORITY = re.compile(r"\bpriority\b", re.I)

BINDING_IDS = frozenset(
    {
        "bind",
        "clamp",
        "constrict",
        "fire-spin",
        "infestation",
        "magma-storm",
        "sand-tomb",
        "whirlpool",
        "wrap",
        "snap-trap",
    }
)
HAZARD_IDS = frozenset({"spikes", "stealth-rock", "sticky-web", "toxic-spikes"})


def distill_keyword(move_id: str, desc: str) -> str | None:
    d = desc or ""
    mid = (move_id or "").lower()

    if RE_REACTION.search(d):
        return "Reaction"
    if RE_SCATTER.search(d):
        return "Scatter"
    if RE_BINDING_MOVE.search(d) or mid in BINDING_IDS:
        return "Binding"
    if RE_MULTITURN.search(d):
        return "Multi-turn"
    if mid.endswith("-terrain") or RE_TERRAIN_CREATE.search(d):
        return "Terrain"
    if RE_WEATHER_CREATE.search(d):
        return "Weather"
    if mid in HAZARD_IDS or RE_HAZARD_PLACE.search(d):
        return "Hazard"
    if RE_COAT_PUT.search(d):
        return "Coat"
    if RE_PRIORITY.search(d):
        return "Priority"
    return None


def rebuild_mechanics(mech: dict, kw: str | None) -> dict:
    effects = mech.get("effects")
    out: dict = {}
    for key in (
        "frequency",
        "accuracy",
        "attack_type",
        "target",
        "target_range",
        "effect_radius",
    ):
        if key in mech:
            out[key] = mech[key]
    if "damage_bonus" in mech:
        out["damage_bonus"] = mech["damage_bonus"]
    out["move_keyword"] = kw
    out["effects"] = effects
    return out


def main() -> int:
    data = json.loads(MOVES.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        print("Expected array", file=sys.stderr)
        return 1
    for m in data:
        mech = m.get("mechanics")
        if not isinstance(mech, dict):
            continue
        kw = distill_keyword(str(m.get("id", "")), str(m.get("description", "")))
        m["mechanics"] = rebuild_mechanics(mech, kw)
    MOVES.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
    tagged = sum(1 for m in data if m.get("mechanics", {}).get("move_keyword") is not None)
    print(f"Updated {len(data)} moves; {tagged} with non-null move_keyword.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
