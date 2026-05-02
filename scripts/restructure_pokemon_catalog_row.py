#!/usr/bin/env python3
"""
Restructure each pokemon.json row: ordered keys, stats object, evolution.to[], habitat/diet/size/weight renames.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POKEMON_JSON = ROOT / "lib" / "pokemon.json"

ORDER = [
    "type",
    "id",
    "national_dex_number",
    "generation",
    "name",
    "rarity",
    "elemental_types",
    "description",
    "gender_rate",
    "egg_group",
    "hatch_time",
    "size",
    "weight",
    "habitat",
    "diet",
    "stats",
    "skills",
    "passives",
    "proficiencies",
    "inherent_moves",
    "evolution_stage",
    "evolved_from",
    "evolution",
    "sprites",
    "is_temporary",
]


def extract_item_id(conditions: str | None) -> str | None:
    if not conditions or not isinstance(conditions, str):
        return None
    m = re.search(
        r"(?:with a|using a)\s+([A-Za-z][A-Za-z'\s-]+?(?:Stone|Stone\b))",
        conditions,
        re.IGNORECASE,
    )
    if not m:
        return None
    name = m.group(1).strip()
    slug = name.lower().replace("'", "").replace(" ", "-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or None


def branch_is_natural(
    details: str | None,
    row_natural: bool | None,
) -> bool:
    if details and isinstance(details, str):
        d = details.lower()
        if "stone" in d or "trade" in d or "traded" in d or "held" in d:
            return False
        if any(
            x in d
            for x in (
                "level",
                "friendship",
                "happiness",
                "beauty",
                "affection",
                "daytime",
                "night",
                "rain",
                "location",
                "party",
                "attack",
                "defense",
                "spin",
                "recoil",
                "empty",
            )
        ):
            return True
    return row_natural is True


def build_evolution(
    row: dict,
) -> dict:
    targets = row.get("evolves_to") or []
    if not isinstance(targets, list):
        targets = []
    details = row.get("evolves_to_details") or {}
    if not isinstance(details, dict):
        details = {}
    rn = row.get("evolves_next_naturally")
    out: list[dict] = []
    for tid in targets:
        tid = str(tid).strip()
        if not tid:
            continue
        cond = details.get(tid)
        cond_s = str(cond).strip() if cond is not None else None
        if cond_s == "":
            cond_s = None
        out.append(
            {
                "id": tid,
                "is_natural": branch_is_natural(cond_s, rn),
                "item": extract_item_id(cond_s),
                "conditions": cond_s,
            }
        )
    return {"to": out}


def reorder_row(row: dict) -> dict:
    stats = {
        "HP": int(row["hp"]),
        "ATK": int(row["atk"]),
        "DEF": int(row["def"]),
        "spATK": int(row["spec_atk"]),
        "spDEF": int(row["spec_def"]),
        "SPD": int(row["speed"]),
    }
    evolution = build_evolution(row)
    evolved_from = row.get("evolves_from")
    if evolved_from is not None and evolved_from != "":
        evolved_from = str(evolved_from).strip()
    else:
        evolved_from = None

    new: dict = {
        "type": row["type"],
        "id": row["id"],
        "national_dex_number": row["national_dex_number"],
        "generation": row["generation"],
        "name": row["name"],
        "rarity": row.get("rarity") or "—",
        "elemental_types": row["elemental_types"],
        "description": row["description"],
        "gender_rate": row["gender_rate"],
        "egg_group": row["egg_group"],
        "hatch_time": row["hatch_time"],
        "size": row.get("size_class") or "—",
        "weight": row.get("weight_class") or "—",
        "habitat": row["habitats"],
        "diet": row["diets"],
        "stats": stats,
        "skills": row["skills"],
        "passives": row["passives"],
        "proficiencies": row["proficiencies"],
        "inherent_moves": row["inherent_moves"],
        "evolution_stage": row["evolution_stage"],
        "evolved_from": evolved_from,
        "evolution": evolution,
        "is_temporary": row["is_temporary"],
    }
    if isinstance(row.get("sprites"), dict):
        new["sprites"] = row["sprites"]
    else:
        new["sprites"] = {
            "default": {
                "sprite": row.get("sprite"),
                "sprite_url": row.get("sprite_url"),
            },
            "shiny": {
                "sprite": row.get("shiny_sprite"),
                "sprite_url": row.get("shiny_sprite_url"),
            },
        }
    # Preserve key order
    ordered = {k: new[k] for k in ORDER if k in new}
    return ordered


def main() -> None:
    data = json.loads(POKEMON_JSON.read_text(encoding="utf-8"))
    out: list = []
    for row in data:
        if not isinstance(row, dict):
            out.append(row)
            continue
        if row.get("type") != "pokemon":
            out.append(row)
            continue
        out.append(reorder_row(row))
    POKEMON_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
    print(f"Wrote {len(out)} rows -> {POKEMON_JSON}")


if __name__ == "__main__":
    main()
