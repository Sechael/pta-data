#!/usr/bin/env python3
"""Nest pokemon.json sprite paths under sprites.default / sprites.shiny with sprite + sprite_url."""

from __future__ import annotations

import json
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


def migrate_row(row: dict) -> dict:
    if row.get("type") != "pokemon":
        return row
    if "sprites" in row and isinstance(row["sprites"], dict):
        return row

    sprite = row.pop("sprite", None)
    shiny_sprite = row.pop("shiny_sprite", None)
    sprite_url = row.pop("sprite_url", None)
    shiny_sprite_url = row.pop("shiny_sprite_url", None)

    row["sprites"] = {
        "default": {
            "sprite": sprite,
            "sprite_url": sprite_url,
        },
        "shiny": {
            "sprite": shiny_sprite,
            "sprite_url": shiny_sprite_url,
        },
    }

    ordered: dict = {}
    for k in ORDER:
        if k in row:
            ordered[k] = row[k]
    for k, v in row.items():
        if k not in ordered:
            ordered[k] = v
    return ordered


def main() -> None:
    data = json.loads(POKEMON_JSON.read_text(encoding="utf-8"))
    out = [migrate_row(r) if isinstance(r, dict) else r for r in data]
    POKEMON_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
    print(f"Updated {POKEMON_JSON}")


if __name__ == "__main__":
    main()
