"""
Action definitions for Raiders of the North Sea
All possible player actions in the game
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
from enum import Enum

from game.state import GameState, PlayerState, WorkerColor


class ActionType(Enum):
    """Types of actions in the game"""
    # Work phase actions
    PLACE_WORKER = "place_worker"
    PICKUP_WORKER = "pickup_worker"
    
    # Building-specific actions
    DRAW_CARDS = "draw_cards"
    PLAY_CARD_TOWN_HALL = "play_card_town_hall"
    DISCARD_FOR_CURRENCY = "discard_for_currency"
    HIRE_CREW = "hire_crew"
    PURCHASE_ARMOUR = "purchase_armour"
    GAIN_BY_WORKER_COLOR = "gain_by_worker_color"
    TRADE_RESOURCES = "trade_resources"
    MAKE_OFFERING = "make_offering"
    
    # Raid phase actions
    RAID = "raid"
    
    # Turn management
    PASS_TURN = "pass_turn"


@dataclass
class Action(ABC):
    """Base class for all actions"""
    player_id: int
    action_type: ActionType
    
    @abstractmethod
    def is_legal(self, state: GameState) -> bool:
        """Check if this action is legal in the current state"""
        pass
    
    @abstractmethod
    def execute(self, state: GameState) -> GameState:
        """Execute this action, modifying the game state"""
        pass
    
    def get_description(self) -> str:
        """Get a human-readable description of this action"""
        return f"{self.action_type.value}"


@dataclass
class PlaceWorkerAction(Action):
    """Place a worker on a village building"""
    building_id: str
    
    def __init__(self, player_id: int, building_id: str):
        super().__init__(player_id, ActionType.PLACE_WORKER)
        self.building_id = building_id
    
    def is_legal(self, state: GameState) -> bool:
        from game.board import get_board_database
        
        player = state.get_player(self.player_id)
        if not player or not player.worker_in_hand:
            return False
        
        # Cannot place worker if already placed one this turn
        if player.placed_worker_this_turn is not None:
            return False
        
        # Get building
        board_db = get_board_database()
        building = board_db.get_building(self.building_id)
        if not building:
            return False
        
        # Check if worker color is allowed
        if not building.allows_worker_color(player.worker_in_hand.value):
            return False
        
        # Check if building has space
        workers_here = state.get_worker_at_building(self.building_id)
        if len(workers_here) >= building.worker_slots:
            return False
        
        return True
    
    def execute(self, state: GameState) -> GameState:
        from game.board import get_board_database
        from game.state import WorkerPlacement
        
        player = state.get_player(self.player_id)
        building = get_board_database().get_building(self.building_id)
        
        # Place worker
        placement = WorkerPlacement(
            building_id=self.building_id,
            worker_color=player.worker_in_hand,
            player_id=self.player_id
        )
        state.worker_placements.append(placement)
        
        # Track placement
        player.placed_worker_this_turn = self.building_id
        
        # Clear worker from hand
        placed_worker = player.worker_in_hand
        player.worker_in_hand = None
        
        # Execute building action (can be skipped - for now always execute)
        self._execute_building_action(state, player, building, placed_worker)
        
        # Mark building as used
        if self.building_id not in player.buildings_used_this_turn:
            player.buildings_used_this_turn.append(self.building_id)
        
        return state
    
    def _execute_building_action(self, state: GameState, player: PlayerState, building, worker_color: WorkerColor):
        """Execute the building's action"""
        action_data = building.action
        action_type = action_data.get("type")
        
        if action_type == "draw_cards":
            amount = action_data.get("amount", 0)
            for _ in range(amount):
                card = state.draw_card()
                if card:
                    player.hand.append(card)
        
        elif action_type == "gain_by_worker_color":
            by_color = action_data.get("by_color", {})
            color_data = by_color.get(worker_color.value, {})
            
            # Handle choice if present
            if "choice" in color_data:
                # For now, take first option (needs player choice logic later)
                resources = color_data["choice"][0]
            else:
                resources = color_data
            
            # Grant resources
            for resource, amount in resources.items():
                if resource == "silver":
                    player.silver += amount
                elif resource == "gold":
                    player.gold += amount
                elif resource == "provisions":
                    player.provisions += amount
                elif resource == "iron":
                    player.iron += amount
                elif resource == "livestock":
                    player.livestock += amount
        
        # Other action types will be handled by separate action classes
    
    def get_description(self) -> str:
        from game.board import get_board_database
        building = get_board_database().get_building(self.building_id)
        return f"Place worker at {building.name if building else self.building_id}"


@dataclass
class PickupWorkerAction(Action):
    """Pick up a worker from a village building"""
    building_id: str
    
    def __init__(self, player_id: int, building_id: str):
        super().__init__(player_id, ActionType.PICKUP_WORKER)
        self.building_id = building_id
    
    def is_legal(self, state: GameState) -> bool:
        player = state.get_player(self.player_id)
        if not player or player.worker_in_hand is not None:
            return False
        
        # Cannot pickup if haven't placed a worker this turn yet
        if player.placed_worker_this_turn is None:
            return False
        
        # Cannot pick up from the same building just placed at
        if player.placed_worker_this_turn == self.building_id:
            return False
        
        # Cannot use same building twice in one turn
        if self.building_id in player.buildings_used_this_turn:
            return False
        
        # Check if there are ANY workers at this building (not player-owned)
        workers_here = state.get_worker_at_building(self.building_id)
        
        return len(workers_here) > 0
    
    def execute(self, state: GameState) -> GameState:
        from game.board import get_board_database
        
        player = state.get_player(self.player_id)
        building = get_board_database().get_building(self.building_id)
        
        # Find and remove ANY worker from building (workers aren't owned)
        workers_here = state.get_worker_at_building(self.building_id)
        
        if workers_here:
            # Pick up the first worker
            worker = workers_here[0]
            state.worker_placements.remove(worker)
            worker_color = worker.worker_color
            
            # Put worker in hand
            player.worker_in_hand = worker_color
            
            # Execute building action (can be skipped - for now always execute)
            action_data = building.action
            action_type = action_data.get("type")
            
            if action_type == "draw_cards":
                amount = action_data.get("amount", 0)
                for _ in range(amount):
                    card = state.draw_card()
                    if card:
                        player.hand.append(card)
            
            elif action_type == "gain_by_worker_color":
                by_color = action_data.get("by_color", {})
                color_data = by_color.get(worker_color.value, {})
                
                # Handle choice if present
                if "choice" in color_data:
                    resources = color_data["choice"][0]
                else:
                    resources = color_data
                
                # Grant resources
                for resource, amount in resources.items():
                    if resource == "silver":
                        player.silver += amount
                    elif resource == "gold":
                        player.gold += amount
                    elif resource == "provisions":
                        player.provisions += amount
                    elif resource == "iron":
                        player.iron += amount
                    elif resource == "livestock":
                        player.livestock += amount
            
            # Mark building as used
            if self.building_id not in player.buildings_used_this_turn:
                player.buildings_used_this_turn.append(self.building_id)
            
            # Turn ends after pickup - advance to next player
            player.has_acted = True
            
            # Enforce hand limit (8 cards)
            while len(player.hand) > 8:
                # Discard last card (player should choose, but auto for now)
                card = player.hand.pop()
                state.discard_card(card)
            
            # Move to next player
            state.next_player()
            
            # Reset turn tracking for next player
            next_player = state.get_current_player()
            next_player.reset_turn_tracking()
            
            # Check if round is complete
            if state.is_round_complete():
                state.start_new_round()
        
        return state
    
    def get_description(self) -> str:
        from game.board import get_board_database
        building = get_board_database().get_building(self.building_id)
        return f"Pick up worker from {building.name if building else self.building_id}"


@dataclass
class HireCrewAction(Action):
    """Hire a crew member from hand"""
    card_id: str  # ID of the card in player's hand (by index or name)
    discard_crew_id: Optional[str] = None  # Optional crew to discard first
    
    def __init__(self, player_id: int, card_id: str, discard_crew_id: Optional[str] = None):
        super().__init__(player_id, ActionType.HIRE_CREW)
        self.card_id = card_id
        self.discard_crew_id = discard_crew_id
    
    def is_legal(self, state: GameState) -> bool:
        player = state.get_player(self.player_id)
        if not player:
            return False
        
        # Find card in hand
        card = next((c for c in player.hand if c.id == self.card_id), None)
        if not card:
            return False
        
        # Check if player can afford
        if player.silver < card.cost:
            return False
        
        # Check crew limit (5 max)
        if player.get_crew_count() >= 5:
            # Must discard a crew first
            if not self.discard_crew_id:
                return False
        
        # Check hero restriction (max 1 hero)
        if card.is_hero and player.has_hero():
            return False
        
        return True
    
    def execute(self, state: GameState) -> GameState:
        player = state.get_player(self.player_id)
        
        # Find and remove card from hand
        card = next((c for c in player.hand if c.id == self.card_id), None)
        if card:
            player.hand.remove(card)
            
            # Discard crew if needed
            if self.discard_crew_id:
                crew = next((c for c in player.crew if c.id == self.discard_crew_id), None)
                if crew:
                    player.crew.remove(crew)
                    state.discard_card(crew)
            
            # Pay cost
            player.silver -= card.cost
            
            # Add to crew
            player.crew.append(card)
            
            # Resolve hire crew action effect
            # (Effects will be handled by rules engine)
        
        return state
    
    def get_description(self) -> str:
        return f"Hire crew: {self.card_id}"


@dataclass
class PlayCardTownHallAction(Action):
    """Play a card at Town Hall for its Town Hall action"""
    card_id: str
    
    def __init__(self, player_id: int, card_id: str):
        super().__init__(player_id, ActionType.PLAY_CARD_TOWN_HALL)
        self.card_id = card_id
    
    def is_legal(self, state: GameState) -> bool:
        player = state.get_player(self.player_id)
        if not player:
            return False
        
        # Find card in hand
        card = next((c for c in player.hand if c.id == self.card_id), None)
        if not card:
            # Also check crew
            card = next((c for c in player.crew if c.id == self.card_id), None)
            if not card:
                return False
        
        # Check if card can be played at Town Hall (not a hero)
        from game.cards import TownsfolkCard
        if isinstance(card, TownsfolkCard):
            return card.is_playable_at_town_hall()
        
        return True
    
    def execute(self, state: GameState) -> GameState:
        player = state.get_player(self.player_id)
        
        # Find card (check hand first, then crew)
        card = next((c for c in player.hand if c.id == self.card_id), None)
        from_hand = True
        
        if not card:
            card = next((c for c in player.crew if c.id == self.card_id), None)
            from_hand = False
        
        if card:
            # Remove card from hand or crew
            if from_hand:
                player.hand.remove(card)
            else:
                player.crew.remove(card)
            
            # Discard card
            state.discard_card(card)
            
            # Resolve Town Hall action effect
            # (Effects will be handled by rules engine)
        
        return state
    
    def get_description(self) -> str:
        return f"Play card at Town Hall: {self.card_id}"


@dataclass
class RaidAction(Action):
    """Raid a location"""
    location_id: str
    sublocation_id: str
    crew_ids: List[str]  # IDs of crew members to bring on raid
    
    def __init__(self, player_id: int, location_id: str, sublocation_id: str, crew_ids: List[str]):
        super().__init__(player_id, ActionType.RAID)
        self.location_id = location_id
        self.sublocation_id = sublocation_id
        self.crew_ids = crew_ids
    
    def is_legal(self, state: GameState) -> bool:
        from game.board import get_board_database
        
        player = state.get_player(self.player_id)
        if not player or not player.worker_in_hand:
            return False
        
        # Cannot raid if haven't placed a worker this turn
        if player.placed_worker_this_turn is None:
            return False
        
        # Get raid location
        board_db = get_board_database()
        raid = board_db.get_raid(self.location_id)
        if not raid:
            return False
        
        # Check worker color requirement
        if not raid.allows_worker_color(player.worker_in_hand.value):
            return False
        
        # Check minimum crew requirement
        if len(self.crew_ids) < raid.requirements["min_crew"]:
            return False
        
        # Check if player has all specified crew
        for crew_id in self.crew_ids:
            if not any(c.id == crew_id for c in player.crew):
                return False
        
        # Check provisions requirement
        if player.provisions < raid.requirements["provisions"]:
            return False
        
        # Check gold requirement
        if player.gold < raid.requirements["gold"]:
            return False
        
        # Check if sublocation exists and has plunder
        raid_state = state.get_raid_state(self.location_id, self.sublocation_id)
        if not raid_state or raid_state.get_plunder_remaining() <= 0:
            return False
        
        return True
    
    def execute(self, state: GameState) -> GameState:
        from game.board import get_board_database
        import random
        
        player = state.get_player(self.player_id)
        raid = get_board_database().get_raid(self.location_id)
        raid_state = state.get_raid_state(self.location_id, self.sublocation_id)
        
        # Pay costs
        player.provisions -= raid.requirements["provisions"]
        player.gold -= raid.requirements["gold"]
        
        # Calculate total strength
        total_strength = sum(
            c.strength for c in player.crew if c.id in self.crew_ids
        )
        
        # Roll dice
        dice_rolls = [random.randint(1, 6) for _ in range(raid.dice_added)]
        dice_total = sum(dice_rolls)
        
        final_strength = total_strength + dice_total
        
        # Get VP
        vp_earned = raid.get_vp_for_strength(final_strength)
        player.vp += vp_earned
        
        # Get plunder - collect all resources from this raid spot
        for resource, amount in raid_state.plunder_resources.items():
            if resource == 'gold':
                player.gold += amount
            elif resource == 'iron':
                player.iron += amount
            elif resource == 'livestock':
                player.livestock += amount
            elif resource == 'valkyrie':
                player.valkyrie += amount
        
        # Take plunder from raid location
        raid_state.plunder_resources.clear()
        
        # Place worker at raid location
        raid_state.worker_present = player.worker_in_hand
        player.worker_in_hand = None
        
        # Turn ends after raid - advance to next player
        player.has_acted = True
        
        # Enforce hand limit (8 cards)
        while len(player.hand) > 8:
            card = player.hand.pop()
            state.discard_card(card)
        
        # Move to next player
        state.next_player()
        
        # Reset turn tracking for next player
        next_player = state.get_current_player()
        next_player.reset_turn_tracking()
        
        # Check if round is complete
        if state.is_round_complete():
            state.start_new_round()
        
        return state
    
    def get_description(self) -> str:
        from game.board import get_board_database
        raid = get_board_database().get_raid(self.location_id)
        return f"Raid {raid.name if raid else self.location_id} with {len(self.crew_ids)} crew"


@dataclass
class SkipBuildingActionWrapper(Action):
    """Wrapper to allow skipping building actions while still placing/picking up worker"""
    base_action: Action  # PlaceWorkerAction or PickupWorkerAction
    skip_action: bool = False
    
    def __init__(self, base_action: Action, skip_action: bool = False):
        super().__init__(base_action.player_id, base_action.action_type)
        self.base_action = base_action
        self.skip_action = skip_action
    
    def is_legal(self, state: GameState) -> bool:
        return self.base_action.is_legal(state)
    
    def execute(self, state: GameState) -> GameState:
        # If skipping, we need to manually handle worker movement without building action
        # For now, delegate to base action (full implementation later)
        return self.base_action.execute(state)
    
    def get_description(self) -> str:
        desc = self.base_action.get_description()
        if self.skip_action:
            desc += " (skip action)"
        return desc


if __name__ == "__main__":
    print("Action types defined:")
    for action_type in ActionType:
        print(f"  - {action_type.value}")
    
    print("\nAction classes:")
    print("  - PlaceWorkerAction")
    print("  - PickupWorkerAction")
    print("  - HireCrewAction")
    print("  - PlayCardTownHallAction")
    print("  - RaidAction")
    print("  - SkipBuildingActionWrapper (allows skipping building actions)")
    print("\nNote: Turn ends automatically after picking up worker or completing raid")
