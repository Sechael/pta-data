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
| `items/*.json`  | Split item catalogs by category (mechanics + conditions) |
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
### Item (`lib/items/medical.json`)

```json
{
  "type": "item",
  "id": "potion",
  "category": "Medical",
  "rarity": "Common",
  "price": 25,
  "is_consumable": true,
  "conditions": ["POKEMON", "CONSCIOUS"],
  "mechanics": [
    { "type": "HEAL", "target": "SELECTED", "value": 10, "resource": "HP" }
  ],
  "sprite_url": "https://…",
  "description": "Spray-type medicine that heals 10 HP for a Pokémon.",
  "name": "Potion",
  "sprite": "items/potion.png",
  "size": "1x1"
}
```

### Item mechanics schema outline

Items are now mechanics-first (see `schemas/itemschema.json` and `lib/items/*.json`).

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
    { "type": "HEAL", "target": "SELECTED", "value": "33%", "resource": "HP" },
    {
      "type": "CONDITION",
      "target": "SELECTED",
      "value": "CURE",
      "resource": "CONFUSION",
      "params": { "exception": "POKEMON_TASTE_LIKE_FLAVORS" }
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

### 0.5.1
- **Monolithic items file removed from the repo:** `lib/items.json` is deleted; consumers use split bundles under `lib/items/*.json` only (this completes the change described for 0.5.0 in documentation).
- **Validation:** `scripts/validate.mjs` now checks every `lib/items/*.json` file instead of a single `lib/items.json` (addresses the 0.5.0 “Open” follow-up).
- **Items data:** `pokeball-container` includes structured `container` metadata (12 units, `BALL`, Pokeball category) per `schemas/itemschema.json`. `lib/items/medical.json` — Hyper Lemonade sprite URL fix, rarity pass (Iron, Max Potion, Revive, Super Potion). `lib/items/supplies.json` — `pokemon-food` and `pokemon-food-bag` prices aligned to current app/economy defaults.

### 0.5.0
- **Items split finalized:** Documented removal of legacy `lib/items.json` in favor of split `lib/items/*.json` as the item source; package exports already targeted split paths.
- **Medical tuning pass:** Updated selected `lib/items/medical.json` entries (including rarity alignment and sprite URL correction) to match current mechanics-first usage in the app.
- **Docs refresh:** README examples and item model notes now describe the active mechanics-first structure (`HEAL` / `CONDITION` / `STAT_MOD`) and split catalog layout.

### 0.4.0
- **Moves** (`lib/moves.json`): optional tactical **`move_keyword`** on each `mechanics` block (`Binding`, `Coat`, `Hazard`, `Multi-turn`, `Priority`, `Reaction`, `Scatter`, `Terrain`, `Weather`, or `null`), placed before `effects`; validated by `schemas/moveschema.json`. Tagging maintained by `scripts/augment_move_keywords.py`.
- **Schemas**: JSON Schemas live under **`schemas/`** (`itemschema.json`, `moveschema.json`); removed duplicate `lib/itemschema.json`. Published tarball includes `schemas/`; **exports** expose `./schemas/itemschema.json` and `./schemas/moveschema.json`.
- **Tooling**: `scripts/migrate_moves_catalog_to_v2.py` documents the legacy → mechanics-bundle migration path.
- **npm**: `0.4.0` is published as `@sechael/pta-data`. In consuming apps, run `npm install` so `package-lock.json` pins `0.4.0` and the registry `integrity` hash.

### 0.3.0
- **Pokémon** (`lib/pokemon.json`): catalog row shape updates (e.g. nested `sprites.default` / `sprites.shiny` with local paths and PokéAPI `sprite_url` values), stat/evolution/id field alignment.
- **Moves** (`lib/moves.json`): migrated to the mechanics bundle shape (`mechanics.frequency`, `accuracy`, ranges, `effects[]`); validated by `schemas/moveschema.json`.
- **Items**: mechanics / schema alignment across `lib/items/*.json` and `schemas/itemschema.json`.
- **Publishing**: `lib/pokemon-gmax.json` removed from the published package; Gigantamax datasets live under `lib/gmax/` in git and are omitted from the npm tarball (`.npmignore`). `package.json` exports include `./lib/items/*` and no longer export the removed gmax JSON entry.
- **Other catalogs**: updates to `afflictions.json`, `type-chart.json`, `weapons.json`, and `trainer-class-move-pools.json` where the app expects newer shapes.
- **Tooling**: maintenance scripts under `scripts/` (including Pokémon catalog migration and `wire_pokemon_json_sprites.py`) and `validate.mjs` adjustments.

### 0.2.0
- Added `lib/items/` per-category items split (staged migration away from monolithic `items.json`).
- Added item JSON Schema (`schemas/itemschema.json`) and began migrating item rows to a `mechanics[]` model (targets, affects, uses, and container metadata).
- **Open todo**: Check Berries, trainer-equipment Held-items, evolution items, key-items for consistencies (Medical, Pokeball, supplies, tm are valid).
