#!/usr/bin/env python3
"""Migrate lib/moves.json from legacy flat combat fields to moveschema v2 (mechanics bundle + effects)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOVES_PATH = ROOT / "lib" / "moves.json"


def parse_mechanics_frequency(raw) -> int | str | None:
    if raw is None:
        return None
    s = str(raw).strip()
    if s == "At-Will":
        return "At-Will"
    if s == "1/day":
        return 1
    if s == "3/day":
        return 3
    if s == "Varies":
        return "Varies"
    return None


def effect_scope_from_attack_target(attack_target: str | None) -> str:
    t = (attack_target or "").strip().lower()
    if t in ("burst", "blast", "beam", "wave", "beam-blast"):
        return "AOE"
    return "FOE"


def build_effects(m: dict) -> list[dict]:
    desc = (m.get("description") or "").lower()
    effects: list[dict] = []

    flat = int(m.get("damage_flat") or 0)
    n = int(m.get("damage_dice_num") or 0)
    d = int(m.get("damage_die_type") or 0)
    atk_tgt = m.get("attack_target")

    if flat > 0:
        fv = str(flat)
        effects.append(
            {
                "type": "DAMAGE",
                "target": effect_scope_from_attack_target(atk_tgt),
                "value": fv,
                "resource": "HP",
                "damage": {"kind": "Flat", "value": fv},
            }
        )
    elif n > 0 and d > 0:
        # Flat +X suffix belongs in mechanics.damage_bonus, not in damage.value
        dv = f"{n}d{d}"
        effects.append(
            {
                "type": "DAMAGE",
                "target": effect_scope_from_attack_target(atk_tgt),
                "value": dv,
                "resource": "HP",
                "damage": {"kind": "Dice", "value": dv},
            }
        )

    if "regain hp" in desc and "half" in desc and "damage" in desc:
        effects.append(
            {
                "type": "HEAL",
                "target": "SELF",
                "value": "half_damage_dealt",
                "resource": "HP",
                "damage": {"kind": "None", "value": ""},
            }
        )
    elif "regain hp" in desc and "damage" in desc and "half" not in desc:
        effects.append(
            {
                "type": "HEAL",
                "target": "SELF",
                "value": "damage_dealt",
                "resource": "HP",
                "damage": {"kind": "None", "value": ""},
            }
        )

    if "lose hp" in desc and "half" in desc and "damage" in desc:
        effects.append(
            {
                "type": "DAMAGE",
                "target": "SELF",
                "value": "half_damage_dealt",
                "resource": "HP",
                "damage": {"kind": "None", "value": ""},
            }
        )

    if not effects:
        effects.append(
            {
                "type": "EFFECT",
                "target": "FOE",
                "value": "see_description",
                "resource": "MOVE",
                "damage": {"kind": "None", "value": ""},
            }
        )

    return effects


def migrate_move(m: dict) -> dict:
    mf = parse_mechanics_frequency(m.get("frequency"))
    if mf is None:
        mf = None

    mechanics: dict = {
        "frequency": mf,
        "accuracy": int(m.get("accuracy_mod") or 0),
        "attack_type": str(m.get("attack_type") or ""),
        "target": str(m.get("attack_target") or ""),
        "target_range": int(m.get("range_value_1") or 0),
        "effect_radius": int(m.get("range_value_2") or 0),
        "effects": build_effects(m),
    }
    bonus = int(m.get("damage_bonus") or 0)
    if bonus != 0:
        mechanics["damage_bonus"] = bonus

    contest = None
    cs, ck = m.get("contest_stat"), m.get("contest_keyword")
    if cs and ck:
        contest = {"stat": str(cs), "keyword": str(ck)}

    out: dict = {
        "type": "move",
        "id": m["id"],
        "name": m["name"],
        "move_type": m.get("move_type") or "",
        "category": m.get("category") or "",
        "description": m.get("description") or "",
    }
    if m.get("proficency"):
        out["proficency"] = m["proficency"]
    out["contest"] = contest
    out["mechanics"] = mechanics
    return out


def main() -> int:
    raw = json.loads(MOVES_PATH.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        print("Expected array", file=sys.stderr)
        return 1
    out = [migrate_move(m) for m in raw]
    MOVES_PATH.write_text(json.dumps(out, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(out)} moves to {MOVES_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
