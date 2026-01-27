"""
Game state representation for Raiders of the North Sea
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set, Tuple
from enum import Enum
import random

from game.cards import TownsfolkCard, get_card_database
from game.board import VillageBuilding, OfferingTile, RaidLocation, get_board_database


class WorkerColor(Enum):
    """Worker colors in the game"""
    BLACK = "black"
    GREY = "grey"
    WHITE = "white"


class GamePhase(Enum):
    """Game phases"""
    WORK = "work"
    RAID = "raid"
    GAME_END = "game_end"


@dataclass
class PlayerState:
    """State for a single player"""
    player_id: int
    name: str
    
    # Resources
    silver: int = 0
    gold: int = 0
    provisions: int = 0
    iron: int = 0
    livestock: int = 0
    
    # Armour track (0-10)
    armour: int = 0
    
    # Valkyrie track
    valkyrie: int = 0
    
    # Victory points
    vp: int = 0
    
    # Cards
    hand: List[TownsfolkCard] = field(default_factory=list)
    crew: List[TownsfolkCard] = field(default_factory=list)
    
    # Offerings collected
    offerings: List[OfferingTile] = field(default_factory=list)
    
    # Worker currently in hand (color)
    worker_in_hand: Optional[WorkerColor] = None
    
    # Has this player taken their turn this round?
    has_acted: bool = False
    
    # Turn tracking (reset at start of each turn)
    placed_worker_this_turn: Optional[str] = None  # Building ID where worker was placed
    buildings_used_this_turn: List[str] = field(default_factory=list)  # Building IDs used
    
    def __post_init__(self):
        """Initialize mutable defaults"""
        if not isinstance(self.hand, list):
            self.hand = []
        if not isinstance(self.crew, list):
            self.crew = []
        if not isinstance(self.offerings, list):
            self.offerings = []
        if not isinstance(self.buildings_used_this_turn, list):
            self.buildings_used_this_turn = []
    
    def get_total_crew_strength(self) -> int:
        """Calculate total strength from all crew"""
        return sum(card.strength for card in self.crew)
    
    def get_hand_size(self) -> int:
        """Get current hand size"""
        return len(self.hand)
    
    def get_crew_count(self) -> int:
        """Get number of hired crew"""
        return len(self.crew)
    
    def has_hero(self) -> bool:
        """Check if player has hired a hero"""
        return any(card.is_hero for card in self.crew)
    
    def reset_turn_tracking(self):
        """Reset turn tracking at start of player's turn"""
        self.placed_worker_this_turn = None
        self.buildings_used_this_turn.clear()
    
    def get_final_vp(self) -> int:
        """Calculate final VP including crew, offerings, and base VP"""
        total = self.vp
        
        # Add VP from crew cards
        total += sum(card.vp for card in self.crew)
        
        # Add VP from offerings
        total += sum(offering.vp for offering in self.offerings)
        
        return total
    
    def __repr__(self) -> str:
        return (f"Player {self.player_id} ({self.name}): "
                f"{self.silver}S {self.gold}G {self.provisions}P | "
                f"{len(self.crew)} crew | {self.vp} VP")


@dataclass
class WorkerPlacement:
    """Represents a worker placed on a building"""
    building_id: str
    worker_color: WorkerColor
    player_id: int


@dataclass
class RaidState:
    """State of a raid sublocation"""
    location_id: str
    sublocation_id: str
    plunder_remaining: int
    worker_present: Optional[WorkerColor]


@dataclass
class GameState:
    """Complete game state"""
    
    # Players
    players: List[PlayerState]
    current_player_idx: int = 0
    first_player_idx: int = 0
    
    # Game phase
    phase: GamePhase = GamePhase.WORK
    round_number: int = 1
    
    # Decks
    townsfolk_deck: List[TownsfolkCard] = field(default_factory=list)
    townsfolk_discard: List[TownsfolkCard] = field(default_factory=list)
    
    # Offering tiles (stack)
    offering_stack: List[OfferingTile] = field(default_factory=list)
    visible_offerings: List[OfferingTile] = field(default_factory=list)  # Top 3 visible
    
    # Board state
    worker_placements: List[WorkerPlacement] = field(default_factory=list)
    raid_states: List[RaidState] = field(default_factory=list)
    
    # Neutral workers in village (for swapping)
    neutral_workers: List[WorkerColor] = field(default_factory=list)
    
    # Resource pools (shared supply)
    valkyrie_pool: int = 18
    gold_pool: int = 18
    silver_pool: int = 32
    iron_pool: int = 18
    livestock_pool: int = 26
    provisions_pool: int = 32
    
    # Game end tracking
    game_ended: bool = False
    winner_id: Optional[int] = None
    
    def __post_init__(self):
        """Initialize mutable defaults"""
        if not isinstance(self.players, list):
            self.players = []
        if not isinstance(self.townsfolk_deck, list):
            self.townsfolk_deck = []
        if not isinstance(self.townsfolk_discard, list):
            self.townsfolk_discard = []
        if not isinstance(self.offering_stack, list):
            self.offering_stack = []
        if not isinstance(self.visible_offerings, list):
            self.visible_offerings = []
        if not isinstance(self.worker_placements, list):
            self.worker_placements = []
        if not isinstance(self.raid_states, list):
            self.raid_states = []
        if not isinstance(self.neutral_workers, list):
            self.neutral_workers = []
    
    @classmethod
    def create_initial_state(cls, player_names: List[str], seed: Optional[int] = None) -> 'GameState':
        """Create initial game state for a new game"""
        if seed is not None:
            random.seed(seed)
        
        # Create players
        players = []
        for i, name in enumerate(player_names):
            player = PlayerState(
                player_id=i,
                name=name,
                silver=2,  # Starting resources
                provisions=0,
                worker_in_hand=WorkerColor.BLACK  # All players start with a black worker
            )
            players.append(player)
        
        # Create and shuffle townsfolk deck
        card_db = get_card_database()
        deck = card_db.create_deck()
        random.shuffle(deck)
        
        # Deal initial hands (5 cards each, then discard 2 to bottom of deck)
        cards_to_bottom = []
        for player in players:
            # Draw 5 cards
            for _ in range(5):
                if deck:
                    player.hand.append(deck.pop())
            
            # Each player discards 2 cards (last 2 for now, should be player choice)
            for _ in range(2):
                if player.hand:
                    discarded = player.hand.pop()
                    cards_to_bottom.append(discarded)
        
        # Place discarded cards face-down at bottom of deck
        deck = cards_to_bottom + deck
        
        # Shuffle and setup offerings
        board_db = get_board_database()
        offerings = board_db.offerings.copy()
        random.shuffle(offerings)
        visible_offerings = [offerings.pop() for _ in range(3) if offerings]
        
        # Initialize raid states
        raid_states = []
        for raid in board_db.raids:
            for subloc in raid.sublocations:
                raid_state = RaidState(
                    location_id=raid.id,
                    sublocation_id=subloc.id,
                    plunder_remaining=subloc.plunder,
                    worker_present=WorkerColor(subloc.worker_on_spot) if subloc.worker_on_spot else None
                )
                raid_states.append(raid_state)
        
        # Create neutral workers for village
        neutral_workers = [
            WorkerColor.GREY,
            WorkerColor.GREY,
            WorkerColor.GREY,
            WorkerColor.WHITE
        ]
        
        # Place initial black workers on Gate House, Town Hall, and Treasury
        initial_placements = []
        gate_house = board_db.get_building_by_name("Gate House")
        town_hall = board_db.get_building_by_name("Town Hall")
        treasury = board_db.get_building_by_name("Treasury")
        
        for building in [gate_house, town_hall, treasury]:
            if building:
                initial_placements.append(WorkerPlacement(
                    building_id=building.id,
                    worker_color=WorkerColor.BLACK,
                    player_id=-1  # -1 indicates neutral worker
                ))
                print(f"Placed neutral black worker on {building.name}")
        
        state = cls(
            players=players,
            current_player_idx=0,
            first_player_idx=0,
            phase=GamePhase.WORK,
            round_number=1,
            townsfolk_deck=deck,
            townsfolk_discard=[],
            offering_stack=offerings,
            visible_offerings=visible_offerings,
            worker_placements=initial_placements,
            raid_states=raid_states,
            neutral_workers=neutral_workers,
            game_ended=False,
            winner_id=None
        )
        
        return state
    
    def get_current_player(self) -> PlayerState:
        """Get the current active player"""
        return self.players[self.current_player_idx]
    
    def get_player(self, player_id: int) -> Optional[PlayerState]:
        """Get player by ID"""
        for player in self.players:
            if player.player_id == player_id:
                return player
        return None
    
    def get_worker_at_building(self, building_id: str) -> List[WorkerPlacement]:
        """Get all workers at a specific building"""
        return [wp for wp in self.worker_placements if wp.building_id == building_id]
    
    def get_raid_state(self, location_id: str, sublocation_id: str) -> Optional[RaidState]:
        """Get raid state for a specific sublocation"""
        for rs in self.raid_states:
            if rs.location_id == location_id and rs.sublocation_id == sublocation_id:
                return rs
        return None
    
    def draw_card(self) -> Optional[TownsfolkCard]:
        """Draw a card from the deck (with reshuffle if needed)"""
        if not self.townsfolk_deck:
            # Reshuffle discard pile into deck
            self.townsfolk_deck = self.townsfolk_discard.copy()
            self.townsfolk_discard.clear()
            random.shuffle(self.townsfolk_deck)
        
        if self.townsfolk_deck:
            return self.townsfolk_deck.pop()
        return None
    
    def discard_card(self, card: TownsfolkCard):
        """Add a card to the discard pile"""
        self.townsfolk_discard.append(card)
    
    def refill_offerings(self):
        """Refill visible offerings to 3"""
        while len(self.visible_offerings) < 3 and self.offering_stack:
            self.visible_offerings.append(self.offering_stack.pop())
    
    def next_player(self):
        """Advance to next player"""
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
    
    def is_round_complete(self) -> bool:
        """Check if all players have acted this round"""
        return all(p.has_acted for p in self.players)
    
    def start_new_round(self):
        """Start a new round"""
        self.round_number += 1
        for player in self.players:
            player.has_acted = False
        self.current_player_idx = self.first_player_idx
        self.phase = GamePhase.WORK
    
    def check_end_conditions(self) -> bool:
        """Check if game should end"""
        # Condition 1: Only 1 plunder left in all Fortresses combined
        fortress_plunder = sum(
            rs.plunder_remaining 
            for rs in self.raid_states 
            if rs.location_id.startswith('raid_008') or  # Fortress 1
               rs.location_id.startswith('raid_009') or  # Fortress 2
               rs.location_id.startswith('raid_010')     # Fortress 3
        )
        if fortress_plunder <= 1:
            self.game_ended = True
            self.determine_winner()
            return True
        
        # Condition 2: Offering draw pile has been emptied
        if not self.offering_stack:
            self.game_ended = True
            self.determine_winner()
            return True
        
        # Condition 3: No Valkyrie left on board
        # TODO: Track total Valkyrie pool when we implement it
        # For now, this is a placeholder
        
        return False
    
    def determine_winner(self):
        """Determine the winner based on final VP"""
        max_vp = -1
        winner = None
        
        for player in self.players:
            final_vp = player.get_final_vp()
            if final_vp > max_vp:
                max_vp = final_vp
                winner = player
        
        if winner:
            self.winner_id = winner.player_id
            self.phase = GamePhase.GAME_END
    
    def get_game_info(self) -> Dict:
        """Get summary information about the game state"""
        return {
            "round": self.round_number,
            "phase": self.phase.value,
            "current_player": self.get_current_player().name,
            "player_count": len(self.players),
            "deck_size": len(self.townsfolk_deck),
            "offerings_left": len(self.offering_stack),
            "game_ended": self.game_ended,
            "winner": self.get_player(self.winner_id).name if self.winner_id is not None else None
        }
    
    def __repr__(self) -> str:
        info = self.get_game_info()
        return (f"GameState(Round {info['round']}, {info['phase']}, "
                f"Player: {info['current_player']}, "
                f"Players: {info['player_count']})")


if __name__ == "__main__":
    # Test creating a game
    print("Creating test game...")
    game = GameState.create_initial_state(["Alice", "Bob", "Charlie"], seed=42)
    
    print(f"\n{game}")
    print(f"\nGame Info: {game.get_game_info()}")
    
    print("\nPlayers:")
    for player in game.players:
        print(f"  {player}")
        print(f"    Hand: {[c.name for c in player.hand]}")
        print(f"    Worker: {player.worker_in_hand}")
    
    print(f"\nDeck: {len(game.townsfolk_deck)} cards")
    print(f"Visible Offerings: {len(game.visible_offerings)}")
    for offer in game.visible_offerings:
        print(f"  - {offer}")
    
    print(f"\nRaid States: {len(game.raid_states)} sublocations")
    print("Example raids:")
    for rs in game.raid_states[:5]:
        print(f"  {rs.location_id}/{rs.sublocation_id}: {rs.plunder_remaining} plunder, worker: {rs.worker_present}")
