# Game Data for Raiders of the North Sea

This folder contains all static game data in JSON format.

## Files

### Cards
- **`cards_townsfolk.json`** - All Townsfolk/Crew cards (when hired, they become crew)
- **`offerings.json`** - Offering tiles (combinations for Valkyrie points)

### Board
- **`board_village.json`** - Village buildings (worker placement locations)
- **`board_raids.json`** - Raid locations (raids)

## How to Fill Out

### 1. Townsfolk/Crew Cards
For each card:
- `id`: Unique ID (e.g., "card_001")
- `name`: Card name
- `cost`: Silver cost to hire
- `strength`: Combat strength for raids (important!)
- `vp`: Victory points at game end
- `effect`: Text description
- `effect_type`: `immediate`, `raid`, `permanent`, or `end_game`
- `effect_details`: Structured data for the engine
- `color_requirement`: `grey`, `black`, or `null` (worker color needed to hire)

**Note:** A Townsfolk card becomes "Crew" when hired by a player.

**Common Effect Types:**
- `gain_resource`: Gain resources
- `trade`: Trade resources
- `draw_cards`: Draw cards
- `strength_bonus`: Extra strength under conditions
- `extra_plunder`: Additional plunder on raids
- `vp_bonus`: VP bonus under conditions

### 2. Offerings
- `requirements`: What you must give (e.g., Silver, Provisions, Crew)
- `valkyrie_points`: How many Valkyrie markers you receive
- `vp`: Victory points

### 3. Village Buildings
Each building has:
- **Place Action**: What happens when placing a worker
- **Pickup Action**: What happens when picking up a worker
- Some buildings require a black worker

### 4. Raid Locations
- `strength_required`: Minimum strength for successful raid
- `worker_requirement`: `grey` or `black`
- `plunder`: What you receive (resources)
- `rewards`: VP and Valkyrie points

## Usage in Code

These files will be loaded by `game/cards.py` and `game/board.py`:

```python
import json

# Example
with open('data/cards_townsfolk.json', 'r', encoding='utf-8') as f:
    townsfolk_data = json.load(f)
```

## Next Steps

1. ✅ Template files created
2. ⏳ **Fill in cards manually** (based on your physical cards)
3. ⏳ Add missing buildings/raids from the rulebook
4. ⏳ Review all `effect_details` - these control the game logic!

## Tips

- **Comments**: You can't write comments in JSON, but fields with "_comment" are ignored
- **Avoid duplicates**: Ensure unique IDs
- **Maintain structure**: The engine relies on this structure
- **Define effects precisely**: The more precise `effect_details`, the easier the implementation
