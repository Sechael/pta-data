#!/usr/bin/env python3
"""
One-shot migration: drop base_species_id, form_name, variant_name from pokemon.json rows;
rename ids to species stem + canonical regional / slugged form suffix.

Apply id_map across lib/**/*.json for evolves_* and other references.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "lib"


def norm(x: object) -> str:
    return (str(x) if x is not None else "default").strip().lower()


def slug_form(raw: object) -> str:
    s = norm(raw)
    typo = {"mechanical possesstion": "mechanical-possession"}
    if s in typo:
        return typo[s]
    s = str(raw).strip().lower().replace("'", "").replace("'", "")
    s = s.replace("%", "")
    return "-".join(s.split())


def species_stem(row: dict) -> str:
    base = str(row["base_species_id"]).strip()
    if base == "flabb":
        return "flabebe"
    return base


# form_name (normalized) -> canonical suffix (non-regional slug fallback unused here)
FORM_REGIONAL = {
    "iron-rich": "hisui",
    "iron rich": "hisui",
    "urban": "galarian",
    "tropical": "alolan",
    "volcanic": "alolan",
    "dead seas": "galarian",
    "forest glade": "galarian",
    "stone ruins": "galarian",
    "badlands": "hisui",
    "massive leek": "galarian",
    "antique": "hisui",
    "spice diet": "galarian",
    "high mountain": "hisui",
    "tundra": "hisui",
    "oil polluted": "galarian",
    "high ground": "paldean",
    "heavy pollution": "galarian",
    "cold climate": "galarian",
    "dark waters": "galarian",
    "remote isles": "galarian",
    "ancient": "hisui",
    "mountainous": "hisui",
    "primal reversion": "primal",
}


ICY_MOUNTAIN = {
    "sandshrew": "alolan",
    "sandslash": "alolan",
    "vulpix": "alolan",
    "ninetales": "alolan",
    "darumaka": "galarian",
    "darmanitan": "galarian",
    "mr-mime": "galarian",
    "zorua": "hisui",
    "zoroark": "hisui",
}


def compute_new_id(row: dict) -> str:
    stem = species_stem(row)
    oid = str(row["id"]).strip()
    fn = norm(row.get("form_name"))
    vn = norm(row.get("variant_name"))

    if fn == "default" and vn == "default":
        return stem

    if vn == "legend":
        return f"{stem}-hisui"

    if fn == "island":
        return f"{stem}-alolan"

    if fn == "icy mountain zen mode" and stem == "darmanitan":
        return "darmanitan-galarian-zen-mode"

    if fn == "icy mountain":
        suf = ICY_MOUNTAIN.get(stem)
        if suf:
            return f"{stem}-{suf}"
        return f"{stem}-{slug_form(row.get('form_name'))}"

    if fn in FORM_REGIONAL:
        return f"{stem}-{FORM_REGIONAL[fn]}"

    if vn != "default":
        return f"{stem}-{slug_form(row.get('variant_name'))}"

    return f"{stem}-{slug_form(row.get('form_name'))}"


def remap_json(obj, id_map: dict[str, str]):
    if isinstance(obj, dict):
        out: dict = {}
        for k, v in obj.items():
            nk = id_map[k] if k in id_map else k
            out[nk] = remap_json(v, id_map)
        return out
    if isinstance(obj, list):
        return [remap_json(x, id_map) for x in obj]
    if isinstance(obj, str) and obj in id_map:
        return id_map[obj]
    return obj


def main() -> None:
    pokemon_path = LIB / "pokemon.json"
    with open(pokemon_path, encoding="utf-8") as f:
        catalog = json.load(f)

    rows = [r for r in catalog if isinstance(r, dict) and r.get("type") == "pokemon"]
    id_map: dict[str, str] = {}
    for r in rows:
        old = r["id"]
        new = compute_new_id(r)
        id_map[old] = new

    # Collision check (multiple olds -> same new)
    rev: dict[str, list[str]] = {}
    for o, n in id_map.items():
        rev.setdefault(n, []).append(o)
    bad = {n: olds for n, olds in rev.items() if len(olds) > 1}
    if bad:
        raise SystemExit(f"Collision in new ids: {bad}")

    new_ids = set(id_map.values())
    if len(new_ids) != len(id_map):
        raise SystemExit("Duplicate target ids")

    for r in rows:
        new_id = id_map[r["id"]]
        r["id"] = new_id
        for k in ("base_species_id", "form_name", "variant_name"):
            r.pop(k, None)

    catalog = remap_json(catalog, id_map)

    with open(pokemon_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=4)
        f.write("\n")

    # Apply mapping to every JSON file under lib (incl. moves, trainer pools, etc.)
    for path in sorted(LIB.rglob("*.json")):
        if path.name == "pokemon.json":
            continue
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            continue
        out = remap_json(data, id_map)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=4)
            f.write("\n")

    print(f"Updated {pokemon_path}; remapped {len(id_map)} ids across lib/**/*.json")
    changed = sum(1 for o, n in id_map.items() if o != n)
    print(f"Renamed entries: {changed}")


if __name__ == "__main__":
    main()
