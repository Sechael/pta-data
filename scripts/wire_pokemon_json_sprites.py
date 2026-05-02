#!/usr/bin/env python3
"""
Wire each Pokémon row so `sprites.default` and `sprites.shiny` include both:
- `sprite`: logical path served from local assets (`sprites/pokemon/...`)
- `sprite_url`: matching PokéAPI raw sprite URL for the same numeric id.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POKEMON_JSON = ROOT / "lib" / "pokemon.json"

POKEAPI_BASE = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon"


def basename_png(path: str | None) -> str | None:
    if not path or not isinstance(path, str):
        return None
    p = path.strip().replace("\\", "/")
    if not p.lower().endswith(".png"):
        return None
    return p.rsplit("/", 1)[-1]


def stem_digits_png(filename: str | None) -> int | None:
    if not filename or not filename.lower().endswith(".png"):
        return None
    stem = filename[:-4]
    if stem.isdigit():
        return int(stem)
    return None


def pokeapi_default_url(basename: str) -> str:
    stem = basename[:-4] if basename.lower().endswith(".png") else basename
    return f"{POKEAPI_BASE}/{stem}.png"


def pokeapi_shiny_url(basename: str) -> str:
    stem = basename[:-4] if basename.lower().endswith(".png") else basename
    return f"{POKEAPI_BASE}/shiny/{stem}.png"


def wire_row(row: dict) -> None:
    dex_raw = row.get("national_dex_number")
    if dex_raw is None:
        return
    dex = int(dex_raw)

    sprites = row.setdefault("sprites", {})
    default = sprites.setdefault("default", {})
    shiny = sprites.setdefault("shiny", {})

    d_url = default.get("sprite_url")
    d_sprite = default.get("sprite")

    explicit_http = isinstance(d_url, str) and d_url.strip().startswith("http")
    spr_path = d_sprite if isinstance(d_sprite, str) and d_sprite.strip() else None

    basename: str
    if spr_path:
        bn = basename_png(spr_path)
        stem = stem_digits_png(bn) if bn else None
        if stem is not None and stem == dex:
            basename = f"{dex}.png"
        elif bn:
            basename = bn
        else:
            basename = f"{dex}.png"
    elif explicit_http:
        m = re.search(r"/(\d+)\.png(?:\?|$)", str(d_url))
        basename = f"{m.group(1)}.png" if m else f"{dex}.png"
    else:
        basename = f"{dex}.png"

    default["sprite"] = f"sprites/pokemon/{basename}"
    if explicit_http:
        default["sprite_url"] = str(d_url).strip()
    else:
        default["sprite_url"] = pokeapi_default_url(basename)

    shiny["sprite"] = f"sprites/pokemon/shiny/{basename}"
    shiny["sprite_url"] = pokeapi_shiny_url(basename)


def main() -> None:
    raw = POKEMON_JSON.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, list):
        print("expected array", file=sys.stderr)
        sys.exit(1)
    for row in data:
        if isinstance(row, dict) and row.get("type") == "pokemon":
            wire_row(row)
    POKEMON_JSON.write_text(
        json.dumps(data, indent=4, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {POKEMON_JSON}")


if __name__ == "__main__":
    main()
