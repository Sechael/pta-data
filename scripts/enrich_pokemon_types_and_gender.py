#!/usr/bin/env python3
"""
One-shot: add type, elemental_types, gender_rate; remove type_1/type_2.
Fetches gender_rate from PokéAPI (species slug / ndex). Requires network + User-Agent.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POKEMON_JSON = ROOT / "lib" / "pokemon.json"

UA = "pta-data-enrich/1.0 (+https://github.com/Sechael/pta-data)"


def fetch_gender_rate(slug_or_num: str | int) -> int | None:
    path = str(slug_or_num).strip()
    if not path:
        return None
    url = f"https://pokeapi.co/api/v2/pokemon-species/{urllib.parse.quote(path, safe='')}/"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            data = json.load(r)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None
    gr = data.get("gender_rate")
    return gr if isinstance(gr, int) else None


def build_elemental_types(row: dict) -> list[str]:
    et: list[str] = []
    t1, t2 = row.get("type_1"), row.get("type_2")
    if t1 is not None and str(t1).strip():
        et.append(str(t1).strip().lower())
    if t2 is not None and str(t2).strip():
        et.append(str(t2).strip().lower())
    return et


def rewrite_row(old: dict, gender_rate: int | None) -> OrderedDict:
    omit = {"type_1", "type_2"}
    prefix = ["base_species_id", "form_name", "variant_name"]
    out: OrderedDict[str, object] = OrderedDict()
    out["type"] = "pokemon"
    out["id"] = old["id"]
    for k in prefix:
        if k in old:
            out[k] = old[k]
    out["elemental_types"] = build_elemental_types(old)
    out["gender_rate"] = gender_rate
    for k, v in old.items():
        if k in omit or k == "id" or k in prefix:
            continue
        out[k] = v
    return out


def main() -> None:
    raw = POKEMON_JSON.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, list):
        sys.exit("pokemon.json: expected array")

    # Unique species keys for cache (prefer base_species_id)
    seen: set[str] = set()
    keys_order: list[str] = []
    for row in data:
        if not isinstance(row, dict):
            continue
        bs = row.get("base_species_id")
        key = str(bs).strip() if bs is not None and str(bs).strip() else str(row.get("id", "")).strip()
        if key and key not in seen:
            seen.add(key)
            keys_order.append(key)

    cache: dict[str, int | None] = {}
    print(f"Fetching gender_rate for {len(keys_order)} unique species keys…", flush=True)
    for i, key in enumerate(keys_order):
        cache[key] = fetch_gender_rate(key)
        if cache[key] is None:
            nd = None
            # try national dex from first row with this base_species_id
            for row in data:
                if not isinstance(row, dict):
                    continue
                bs = row.get("base_species_id")
                k = str(bs).strip() if bs is not None and str(bs).strip() else str(row.get("id", "")).strip()
                if k != key:
                    continue
                n = row.get("national_dex_number")
                if isinstance(n, (int, float)) and n == n:
                    nd = int(n)
                    break
            if nd is not None:
                cache[key] = fetch_gender_rate(nd)
        time.sleep(0.035)
        if (i + 1) % 100 == 0:
            print(f"  …{i + 1}/{len(keys_order)}", flush=True)

    missing = [k for k, v in cache.items() if v is None]
    if missing:
        print(f"[warn] {len(missing)} species keys still missing gender_rate after ndex fallback", flush=True)
        print("  sample:", missing[:15], flush=True)

    out_rows: list[OrderedDict[str, object]] = []
    for row in data:
        if not isinstance(row, dict):
            continue
        bs = row.get("base_species_id")
        key = str(bs).strip() if bs is not None and str(bs).strip() else str(row.get("id", "")).strip()
        gr = cache.get(key)
        if gr is None:
            gr = fetch_gender_rate(row.get("id"))
        out_rows.append(rewrite_row(row, gr))

    POKEMON_JSON.write_text(json.dumps(out_rows, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(out_rows)} rows to {POKEMON_JSON}")


if __name__ == "__main__":
    main()
