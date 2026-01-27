# Raiders of the North Sea - RL Training Tool

A reinforcement learning tool to discover optimal winning strategies in Raiders of the North Sea board game.

## Project Status

### Completed
- **Project structure** - All directories created
- **JSON data files** - Complete game data loaded:
  - `data/cards_townsfolk.json` - All 26 Townsfolk/Crew cards with effects
  - `data/board_village.json` - All 8 village buildings with actions
  - `data/offerings.json` - All 16 offering tiles
  - `data/board_raids.json` - All 10 raid locations (3 Harbors, 2 Outposts, 2 Monasteries, 3 Fortresses)

### In Progress
- Game engine implementation

### Planned
- RL environment
- Self-play training
- Analytics system
- Human vs AI interface

## Project Architecture (High Level)
/Raiders_of_the_north_sea
│
├── data/
│   ├── cards_townsfolk.json  # ✅ 26 cards complete
│   ├── board_village.json    # ✅ 8 buildings complete
│   ├── offerings.json        # ✅ 16 offerings complete
│   ├── board_raids.json      # ✅ 10 raid locations complete
│   └── README.md             # Data filling instructions
│
├── game/
│   ├── state.py          # complete game state
│   ├── rules.py          # rule engine
│   ├── actions.py        # formal action definitions
│   ├── cards.py          # Townsfolk, Crew, Offerings
│   ├── board.py          # Village + Raids
│   └── engine.py         # turn loop, end conditions
│
├── agents/
│   ├── random_agent.py
│   ├── heuristic_agent.py
│   ├── rl_agent.py
│
├── rl_env/
│   └── raiders_env.py
│
├── training/
│   ├── selfplay.py
│   ├── train.py
│
├── analytics/
│   ├── logger.py
│   ├── stats.py
│   └── visualization.py
│
├── ui/
│   └── gui.py
│
└── README.md

## Game Data Summary

### Townsfolk/Crew Cards (26 total)
- **Heroes (3):** Brynjar, Folke, Ragnhildr (cannot be discarded at Town Hall)
- **Regular Crew (23):** Various costs (1-4 silver), strength (0-4), with Hire Crew and Town Hall actions
- Card effects include: raid bonuses, dynamic strength, trading, stealing, resource generation

### Village Buildings (8 total)
- **No restrictions:** Gate House, Town Hall, Treasury, Barracks, Mill, Silversmith
- **Grey/White only:** Armoury, Long House
- Each building action triggers on both worker placement AND pickup

### Offerings (16 total)
- Cost combinations of gold, iron, livestock, silver
- VP rewards: 2-6 points
- Collected at Long House

### Raid Locations (10 total)
- **Harbors (3):** 1 VP, no dice, 2-3 crew required
- **Outposts (2):** 2-4 VP, +1 die, 3 crew required
- **Monasteries (2):** 4-6 VP, +2 dice, 3-4 crew required, costs 1 gold
- **Fortresses (3):** 5-12 VP, +2 dice, 4-5 crew required, costs 1-2 gold
- Each location has 2-3 sublocations with varying plunder

## Phase 1 – Game Engine (Deterministic + Simulative)
## Goal

A fully rule-compliant simulation without UI.

## Core Concepts

### Game State (GameState)

Contains:

**Player:**
- Resources (Silver, Provisions, Plunder)
- Hand cards
- Crew
- Armour
- Valkyrie Track
- VP (Victory Points)
- Worker in Hand

**Board:**
- Village buildings + occupied workers
- Raiding spaces incl. plunder
- Card decks
- Offering tiles
- Round counter + end conditions

### Actions

Formalized as discrete actions:

**Work Phase:**
- PlaceWorker(building)
- PickupWorker(building)
- PlayCard(card)
- HireCrew(card)
- BuyArmour(...)
- TakeResources(...)

**Raid Phase:**
- Raid(settlement, worker_color)

**All actions must:**
- ✔ Be validated for legality
- ✔ Transform the GameState

### Critical Design Decision

Strictly separate:
- Rule logic (pure functions)
- State (immutable or controlled mutation)

This is crucial for RL + Replays + Debugging.

Phase 2 – Reinforcement Learning Environment
## Goal

Compatible with Gymnasium/OpenAI Gym style.

```python
obs, reward, done, info = env.step(action)
```

### Observation Space

Recommended: Vectorized + normalized.

**Example features:**
- Own resources
- Opponent resources (aggregated or individual)
- Crew composition
- Available worker placements
- Remaining plunder
- Offering tiles
- Game phase

**Optional:**
Separate feature groups (Board, Player, Global)

### Action Space

Discrete, e.g.:
```
0-20   Work actions
21-40  Raid actions
...
```

Or hierarchical (Advanced):
1. First select phase
2. Then select concrete action

### Reward Design

**Minimal start:**
- Final VP difference

**Later reward shaping:**
- VP during game
- Efficient raids
- Offering completion

Avoid excessive shaping → AI might learn wrong strategies.

Phase 3 – Self-Play Training
## Process

- AI plays thousands of games against itself
- Policy is improved after each batch

**Optional enhancements:**
- Elo ranking of agents
- Population Based Training

### Recommended Algorithms

**Start simple:**
- PPO (stable-baselines3)

**Later potentially:**
- AlphaZero-style (MCTS + NN)

Phase 4 – Statistics & Analysis
## Data Collection per Game

**Separated by player count (2/3/4 players):**

### Actions
**Frequency:**
- Worker placement (buildings)
- Worker pickup
- Raid types

### Cards
- Played Townsfolk
- Hired Crew

### Combinations
- Action A → Action B
- Card + following action
- Crew combinations

### Success Metrics
- Winrate per action
- Winrate per card
- Winrate per combination

**Examples:**
- Raid Monastery with >=20 Strength → 63% Winrate
- Sage + Offering Rush → 71% Winrate

### Tools
- pandas
- matplotlib / seaborn
- optional: Jupyter notebooks

Phase 5 – Human vs AI Mode
## Features

### Display
Current game state
Resources
Crew

### AI Capabilities
Calculates:
- Win probability (Value Network)
- Best action (Policy)

**Example output:**
```
Win chance:
You: 42%
AI: 58%

Recommended move:
Place worker at Silversmith → Pickup Town Hall
(Expected value +1.7 VP)
```

## 🖥 UI

**Technology:**
- pygame

**Critical:**
- Only visualize state
- Pass inputs to engine

Extensions (Optional Later)

- Board game expansions
- Human heuristic agents
- Explainable AI (why is this move recommended?)
- Replay viewer

## Testing

**Essential:**
- Unit tests for rules
- Deterministic seeds
- Replayability

**Example tests:**
- Resources never negative
- Illegal moves blocked
- End conditions correct


## Key Success Factors

- Clean state representation
- Separation of logic & presentation
- Start simple, then iteratively refine
- First random + heuristics → then RL