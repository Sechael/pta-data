# @sechael/pta-data

Canonical **PTA catalog** JSON for the **[pta-app](https://github.com/Sechael/pta-app)** compendium: Pokémon, moves, items, weapons, afflictions, type chart, mega/gmax variants, and trainer move pools.

| | |
|--|--|
| **npm** | [`@sechael/pta-data`](https://www.npmjs.com/package/@sechael/pta-data) |
| **Source** | [`github.com/Sechael/pta-data`](https://github.com/Sechael/pta-data) |

---

## Layout (`lib/`)

| File  | Purpose |
|------|----------------|
| `pokemon.json`  | Species / forms |
| `moves.json`  | Moves |
| `items.json`  | Items |
| `weapons.json`  | Trainer weapons |
| `afflictions.json` | Affliction rules |
| `type-chart.json` | Type effectiveness |
| `trainer-class-move-pools.json` | Object | Class move pools (e.g. Martial Form) |
| `pokemon-mega.json`  | Mega forms |
| `pokemon-gmax.json`  | Gigantamax forms |

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

### Move (`lib/moves.json`)

```json
{
  "id": "absorb",
  "attack_type": "melee",
  "attack_target": "Single",
  "range_value_1": 0,
  "range_value_2": 0,
  "move_type": "Grass",
  "category": "Special",
  "frequency": "3/day",
  "accuracy_mod": 0,
  "damage_dice_num": 2,
  "damage_die_type": 8,
  "damage_bonus": 0,
  "contest_stat": "Clever",
  "contest_keyword": "Good Show!",
  "description": "On hit, you regain HP equal to half of the damage dealt.",
  "name": "Absorb",
  "proficency": ["Grass", "Parasitic"]
}
```
