# @sechael/pta-data

Canonical **PTA catalog** JSON for the **[pta-app](https://github.com/Sechael/pta-app)** compendium: Pokémon, moves, items, weapons, afflictions, type chart, mega variants, and trainer move pools. Gigantamax / Dynamax datasets live under `lib/gmax/` in git only (not published on npm until a separate package ships).

| | |
|--|--|
| **npm** | [`@sechael/pta-data`](https://www.npmjs.com/package/@sechael/pta-data) |
| **Source** | [`github.com/Sechael/pta-data`](https://github.com/Sechael/pta-data) |

---

## Layout (`lib/` + `schemas/`)

| File  | Purpose |
|------|----------------|
| `pokemon.json`  | Species / forms |
| `moves.json`  | Moves (mechanics bundle; see `schemas/moveschema.json`) |
| `items.json`  | Items |
| `weapons.json`  | Trainer weapons |
| `afflictions.json` | Affliction rules |
| `type-chart.json` | Type effectiveness |
| `trainer-class-move-pools.json` | Object | Class move pools (e.g. Martial Form) |
| `pokemon-mega.json`  | Mega forms |
| `gmax/*.json` | Gigantamax Pokémon, G-Max moves, related items — **not** in the npm tarball (see `.npmignore`) |

| Path (`schemas/`) | Purpose |
|---------------------|---------|
| `itemschema.json` | JSON Schema for forward-looking item rows + `mechanics` |
| `moveschema.json` | JSON Schema for `moves.json` entries |

---

## Data samples

### Pokémon (`lib/pokemon.json`)

```json
{
  "id": "bulbasaur",
  "base_species_id": "bulbasaur",
  "form_name": "default",
  "variant_name": "default",
  "type_1": "grass",
  "type_2": "poison",
  "egg_group": "['grass', 'monster']",
  "hatch_time": 10,
  "is_temporary": false,
  "gmax_move": null,
  "hp": 30.0,
  "atk": 5.0,
  "def": 4.0,
  "spec_atk": 7.0,
  "spec_def": 7.0,
  "speed": 5.0,
  "evolution_stage": 1.0,
  "evolves_from": null,
  "skills": "['sprouter', 'threaded']",
  "passives": "['growl', 'overgrow']",
  "proficiencies": "['grass', 'poison', 'floral']",
  "inherent_moves": ["tackle", "leech-seed", "vine-whip"],
  "habitats": "['forest', 'jungle']",
  "diets": "['phototroph']",
  "national_dex_number": 1.0,
  "name": "Bulbasaur",
  "description": "…",
  "sprite": "sprites/pokemon/1.png",
  "evolves_to": ["ivysaur"],
  "evolves_next_naturally": true,
  "generation": 1,
  "rarity": "Rare",
  "size_class": "Small",
  "weight_class": "Light"
}
```
### Item (`lib/items.json`)

```json
{
  "id": "wepear-berry",
  "category": "Berry",
  "rarity": "Common",
  "price": 120,
  "effect_type": "NONE",
  "effect_value": 0,
  "is_percentage": false,
  "is_consumable": true,
  "flavors": "[\"Bitter\", \"Sour\"]",
  "sprite_url": "https://…",
  "description": "A common berry.",
  "name": "Wepear Berry",
  "sprite": "items/wepear-berry.png",
  "size": "1x1"
}
```

### Item (new mechanics schema outline)

This repo is migrating items toward a mechanics-based model (see `schemas/itemschema.json`).

```json
{
  "id": "wiki-berry",
  "name": "Wiki Berry",
  "description": "…",
  "category": "Berry",
  "rarity": "Uncommon",
  "price": 850,
  "is_consumable": true,
  "size": "1x1",
  "sprite": "items/wiki-berry.png",
  "sprite_url": "https://…",
  "flavors": ["Dry"],
  "mechanics": [
    { "action": "CURE_HP", "target": "SELECTED_POKEMON", "value": 33, "is_percentage": true },
    {
      "action": "ADD_AFFLICTION",
      "target": "SELECTED_POKEMON",
      "affect": "CONFUSION",
      "exception": { "kind": "POKEMON_TASTE_LIKE_FLAVORS" }
    }
  ],
  "container": {
    "capacity": 12,
    "unit": "BALL",
    "allowed": { "categories": ["Pokeball"] }
  }
}
```

### Move (`lib/moves.json`)

```json
{
  "type": "move",
  "id": "absorb",
  "name": "Absorb",
  "move_type": "Grass",
  "category": "Special",
  "description": "On hit, you regain HP equal to half of the damage dealt.",
  "proficency": ["Grass", "Parasitic"],
  "contest": { "stat": "Clever", "keyword": "Good Show!" },
  "mechanics": {
    "frequency": 3,
    "accuracy": 0,
    "attack_type": "melee",
    "target": "Single",
    "target_range": 0,
    "effect_radius": 0,
    "move_keyword": null,
    "effects": [
      {
        "type": "DAMAGE",
        "target": "FOE",
        "value": "2d8",
        "resource": "HP",
        "damage": { "kind": "Dice", "value": "2d8" }
      },
      {
        "type": "HEAL",
        "target": "SELF",
        "value": "half_damage_dealt",
        "resource": "HP",
        "damage": { "kind": "None", "value": "" }
      }
    ]
  }
}
```

---

## Version history

### 0.4.0
- **Moves** (`lib/moves.json`): optional tactical **`move_keyword`** on each `mechanics` block (`Binding`, `Coat`, `Hazard`, `Multi-turn`, `Priority`, `Reaction`, `Scatter`, `Terrain`, `Weather`, or `null`), placed before `effects`; validated by `schemas/moveschema.json`. Tagging maintained by `scripts/augment_move_keywords.py`.
- **Schemas**: JSON Schemas live under **`schemas/`** (`itemschema.json`, `moveschema.json`); removed duplicate `lib/itemschema.json`. Published tarball includes `schemas/`; **exports** expose `./schemas/itemschema.json` and `./schemas/moveschema.json`.
- **Tooling**: `scripts/migrate_moves_catalog_to_v2.py` documents the legacy → mechanics-bundle migration path.
- **npm**: `0.4.0` is published as `@sechael/pta-data`. In consuming apps, run `npm install` so `package-lock.json` pins `0.4.0` and the registry `integrity` hash.

### 0.3.0
- **Pokémon** (`lib/pokemon.json`): catalog row shape updates (e.g. nested `sprites.default` / `sprites.shiny` with local paths and PokéAPI `sprite_url` values), stat/evolution/id field alignment.
- **Moves** (`lib/moves.json`): migrated to the mechanics bundle shape (`mechanics.frequency`, `accuracy`, ranges, `effects[]`); validated by `schemas/moveschema.json`.
- **Items**: mechanics / schema alignment across `lib/items/*.json`, `schemas/itemschema.json`, and the root `lib/items.json` aggregate.
- **Publishing**: `lib/pokemon-gmax.json` removed from the published package; Gigantamax datasets live under `lib/gmax/` in git and are omitted from the npm tarball (`.npmignore`). `package.json` exports include `./lib/items/*` and no longer export the removed gmax JSON entry.
- **Other catalogs**: updates to `afflictions.json`, `type-chart.json`, `weapons.json`, and `trainer-class-move-pools.json` where the app expects newer shapes.
- **Tooling**: maintenance scripts under `scripts/` (including Pokémon catalog migration and `wire_pokemon_json_sprites.py`) and `validate.mjs` adjustments.

### 0.2.0
- Added `lib/items/` per-category items split (staged migration away from monolithic `items.json`).
- Added item JSON Schema (`schemas/itemschema.json`) and began migrating item rows to a `mechanics[]` model (targets, affects, uses, and container metadata).
- **Open todo**: Check Berries, trainer-equipment Held-items, evolution items, key-items for consistencies (Medical, Pokeball, supplies, tm are valid).
