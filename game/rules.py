"""
Rules engine for Raiders of the North Sea
Handles validation, effect resolution, and legal move generation
"""
from typing import List, Optional, Dict, Any, Callable
import random

from game.state import GameState, PlayerState, WorkerColor, GamePhase
from game.cards import TownsfolkCard, get_card_database
from game.board import get_board_database
from game.actions import (
    Action, PlaceWorkerAction, PickupWorkerAction, 
    HireCrewAction, PlayCardTownHallAction, RaidAction
)


class RulesEngine:
    """Centralized rules engine for game logic"""
    
    def __init__(self):
        self.card_db = get_card_database()
        self.board_db = get_board_database()
    
    # ============================================================
    # Legal Move Generation
    # ============================================================
    
    def get_legal_actions(self, state: GameState) -> List[Action]:
        """Get all legal actions for the current player"""
        player = state.get_current_player()
        legal_actions = []
        
        # Turn structure: Player chooses WORK or RAID at start
        # WORK: Place worker on building -> Pick up worker from different building
        # RAID: Complete raid sequence (place, pay, roll, pickup all in RaidAction)
        
        if player.placed_worker_this_turn is None:
            # PHASE 1: Choose action type (must have worker in hand)
            if player.worker_in_hand:
                # Option A: Start WORK sequence by placing worker on building
                legal_actions.extend(self._get_legal_place_actions(state, player))
                
                # Option B: Do RAID sequence (complete action, no pickup after)
                legal_actions.extend(self._get_legal_raid_actions(state, player))
        else:
            # PHASE 2: Finish WORK sequence by picking up worker
            # (Player chose WORK by placing worker, now must pickup)
            legal_actions.extend(self._get_legal_pickup_actions(state, player))
        
        # No pass action - turn ends automatically after pickup or raid
        
        return legal_actions
    
    def _get_legal_place_actions(self, state: GameState, player: PlayerState) -> List[PlaceWorkerAction]:
        """Get all legal worker placement actions"""
        legal = []
        
        for building in self.board_db.buildings:
            action = PlaceWorkerAction(player.player_id, building.id)
            if action.is_legal(state):
                legal.append(action)
        
        return legal
    
    def _get_legal_pickup_actions(self, state: GameState, player: PlayerState) -> List[PickupWorkerAction]:
        """Get all legal worker pickup actions"""
        legal = []
        
        for building in self.board_db.buildings:
            action = PickupWorkerAction(player.player_id, building.id)
            if action.is_legal(state):
                legal.append(action)
        
        return legal
    
    def _get_legal_raid_actions(self, state: GameState, player: PlayerState) -> List[RaidAction]:
        """Get all legal raid actions"""
        legal = []
        
        # For each raid location
        for raid in self.board_db.raids:
            # For each sublocation
            for subloc in raid.sublocations:
                # Try different crew combinations
                # For simplicity, try taking all crew
                if len(player.crew) >= raid.requirements["min_crew"]:
                    crew_ids = [c.id for c in player.crew[:raid.requirements["min_crew"]]]
                    action = RaidAction(player.player_id, raid.id, subloc.id, crew_ids)
                    if action.is_legal(state):
                        legal.append(action)
        
        return legal
    
    # ============================================================
    # Building Action Resolution
    # ============================================================
    
    def execute_building_action(self, state: GameState, player: PlayerState, 
                               building_id: str, worker_color: WorkerColor) -> GameState:
        """Execute a building's action"""
        building = self.board_db.get_building(building_id)
        if not building:
            return state
        
        action_data = building.action
        action_type = action_data.get("type")
        
        if action_type == "draw_cards":
            self._resolve_draw_cards(state, player, action_data)
        
        elif action_type == "play_card_town_hall":
            # This is handled by PlayCardTownHallAction
            pass
        
        elif action_type == "discard_for_currency":
            # This requires player choice - handled by UI/agent
            pass
        
        elif action_type == "hire_crew":
            # This is handled by HireCrewAction
            pass
        
        elif action_type == "purchase_armour":
            # Requires player choice
            pass
        
        elif action_type == "gain_by_worker_color":
            self._resolve_gain_by_worker_color(state, player, action_data, worker_color)
        
        elif action_type == "choose_action":
            # Requires player choice (Long House)
            pass
        
        return state
    
    def _resolve_draw_cards(self, state: GameState, player: PlayerState, action_data: Dict):
        """Resolve drawing cards"""
        amount = action_data.get("amount", 0)
        for _ in range(amount):
            card = state.draw_card()
            if card:
                player.hand.append(card)
    
    def _resolve_gain_by_worker_color(self, state: GameState, player: PlayerState, 
                                     action_data: Dict, worker_color: WorkerColor):
        """Resolve resource gain based on worker color"""
        by_color = action_data.get("by_color", {})
        color_data = by_color.get(worker_color.value, {})
        
        # Handle choice if present
        if "choice" in color_data:
            # For now, take first option (needs player choice logic later)
            resources = color_data["choice"][0]
        else:
            resources = color_data
        
        # Grant resources
        self._grant_resources(player, resources)
    
    def _grant_resources(self, player: PlayerState, resources: Dict[str, int]):
        """Grant resources to a player"""
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
    
    # ============================================================
    # Card Effect Resolution
    # ============================================================
    
    def resolve_hire_crew_effect(self, state: GameState, player: PlayerState, card: TownsfolkCard):
        """Resolve the hire crew action effect of a card"""
        effect = card.hire_crew_action
        effect_type = effect.get("type")
        
        # Most hire crew effects are passive or trigger during raids
        # Store them for later resolution
        
        if effect_type == "end_game":
            # These are calculated at game end
            pass
        
        elif effect_type == "building_bonus":
            # Passive bonus for specific buildings
            pass
        
        elif effect_type == "raid_bonus":
            # Applied during raids
            pass
        
        elif effect_type == "dynamic_strength":
            # Strength calculated during raids
            pass
        
        # Some effects are immediate
        # (None of the current cards have immediate hire effects)
    
    def resolve_town_hall_effect(self, state: GameState, player: PlayerState, card: TownsfolkCard):
        """Resolve the Town Hall action effect of a card"""
        effect = card.town_hall_action
        effect_type = effect.get("type")
        
        if effect_type == "swap_worker":
            # Archer: Swap opponent worker with village worker
            # Requires player choice - placeholder for now
            pass
        
        elif effect_type == "gain_resource":
            resource = effect.get("resource")
            amount = effect.get("amount", 1)
            if resource == "armour":
                player.armour = min(10, player.armour + amount)
            elif resource == "provisions":
                player.provisions += amount
            else:
                self._grant_resources(player, {resource: amount})
        
        elif effect_type == "gain_resources":
            resources = effect.get("resources", {})
            self._grant_resources(player, resources)
        
        elif effect_type == "opponents_lose_resource":
            # Force all opponents to lose resource
            resource = effect.get("resource")
            amount = effect.get("amount", 1)
            for other_player in state.players:
                if other_player.player_id != player.player_id:
                    self._take_resource(other_player, resource, amount)
        
        elif effect_type == "opponent_loses_resource":
            # Force one opponent to lose resource (requires choice)
            pass
        
        elif effect_type == "steal_plunder" or effect_type == "steal_resource":
            # Take from opponent (requires choice)
            pass
        
        elif effect_type == "trade":
            # Trade resources
            give = effect.get("give", {})
            receive = effect.get("receive", {})
            # Check if player has resources to give
            if self._has_resources(player, give):
                self._take_resources(player, give)
                self._grant_resources(player, receive)
        
        elif effect_type == "draw_cards":
            amount = effect.get("amount", 0)
            for _ in range(amount):
                card = state.draw_card()
                if card:
                    player.hand.append(card)
        
        elif effect_type == "swap_crew_card":
            # Gravedigger: Swap crew with hand card (requires choice)
            pass
        
        elif effect_type == "discard_for_currency":
            # Treasury-like effect (requires choice)
            pass
        
        elif effect_type == "hire_crew_discounted":
            # Recruiter: Hire crew for reduced cost (requires choice)
            pass
        
        elif effect_type == "manipulate_offerings":
            # Sage: Move offerings to bottom
            if len(state.visible_offerings) == 3:
                # Move all 3 to bottom of stack
                for offering in state.visible_offerings[:]:
                    state.offering_stack.insert(0, offering)
                state.visible_offerings.clear()
                state.refill_offerings()
        
        elif effect_type == "swap_cards_opponent":
            # Scout: Swap cards with opponent (requires choice)
            pass
        
        elif effect_type == "offering_discount":
            # Trader: Make offering with discount (requires choice)
            pass
        
        elif effect_type == "collect_from_opponents":
            # Mercenary: All players give you resource
            options = effect.get("options", [])
            amount = effect.get("amount", 1)
            # For now, randomly choose what each opponent gives
            for other_player in state.players:
                if other_player.player_id != player.player_id:
                    chosen_resource = random.choice(options)
                    if self._has_resources(other_player, {chosen_resource: amount}):
                        self._take_resource(other_player, chosen_resource, amount)
                        self._grant_resources(player, {chosen_resource: amount})
        
        elif effect_type == "copy_building_action":
            # Merchant: Use any building action (requires choice)
            pass
    
    def calculate_raid_strength(self, state: GameState, player: PlayerState, 
                                crew_ids: List[str], raid_location_id: str) -> int:
        """Calculate total strength for a raid including bonuses"""
        total_strength = 0
        
        # Get selected crew
        selected_crew = [c for c in player.crew if c.id in crew_ids]
        
        for card in selected_crew:
            base_strength = card.strength
            
            # Apply dynamic strength bonuses
            effect = card.hire_crew_action
            effect_type = effect.get("type")
            
            if effect_type == "dynamic_strength":
                condition = effect.get("condition")
                
                if condition == "armour_count":
                    divisor = effect.get("divisor", 1)
                    bonus_per = effect.get("bonus_per", 1)
                    bonus = (player.armour // divisor) * bonus_per
                    base_strength += bonus
                
                elif condition == "crew_count":
                    bonus_per = effect.get("bonus_per", 1)
                    # Count other crew
                    other_crew = len([c for c in selected_crew if c.id != card.id])
                    bonus = other_crew * bonus_per
                    base_strength += bonus
                
                elif condition == "valkyrie_count":
                    divisor = effect.get("divisor", 1)
                    bonus_per = effect.get("bonus_per", 1)
                    bonus = (player.valkyrie // divisor) * bonus_per
                    base_strength += bonus
            
            # Apply raid-specific strength bonuses
            elif effect_type == "raid_strength_bonus":
                raid = self.board_db.get_raid(raid_location_id)
                if raid:
                    condition = effect.get("condition")
                    if condition == "raid_type":
                        raid_type = effect.get("raid_type")
                        if raid.type == raid_type:
                            bonus = effect.get("bonus", 0)
                            base_strength += bonus
            
            total_strength += base_strength
        
        return total_strength
    
    # ============================================================
    # Helper Methods
    # ============================================================
    
    def _has_resources(self, player: PlayerState, resources: Dict[str, int]) -> bool:
        """Check if player has required resources"""
        for resource, amount in resources.items():
            if resource == "silver" and player.silver < amount:
                return False
            elif resource == "gold" and player.gold < amount:
                return False
            elif resource == "provisions" and player.provisions < amount:
                return False
            elif resource == "iron" and player.iron < amount:
                return False
            elif resource == "livestock" and player.livestock < amount:
                return False
        return True
    
    def _take_resources(self, player: PlayerState, resources: Dict[str, int]):
        """Remove resources from player"""
        for resource, amount in resources.items():
            self._take_resource(player, resource, amount)
    
    def _take_resource(self, player: PlayerState, resource: str, amount: int):
        """Remove a specific resource from player"""
        if resource == "silver":
            player.silver = max(0, player.silver - amount)
        elif resource == "gold":
            player.gold = max(0, player.gold - amount)
        elif resource == "provisions":
            player.provisions = max(0, player.provisions - amount)
        elif resource == "iron":
            player.iron = max(0, player.iron - amount)
        elif resource == "livestock":
            player.livestock = max(0, player.livestock - amount)
    
    def check_game_end(self, state: GameState) -> bool:
        """Check if game should end"""
        return state.check_end_conditions()
    
    def validate_action(self, state: GameState, action: Action) -> bool:
        """Validate if an action is legal"""
        return action.is_legal(state)
    
    def apply_action(self, state: GameState, action: Action) -> GameState:
        """Apply an action to the game state"""
        if not self.validate_action(state, action):
            raise ValueError(f"Illegal action: {action.get_description()}")
        
        return action.execute(state)


# Singleton instance
_rules_engine: Optional[RulesEngine] = None

def get_rules_engine() -> RulesEngine:
    """Get or create the rules engine singleton"""
    global _rules_engine
    if _rules_engine is None:
        _rules_engine = RulesEngine()
    return _rules_engine


if __name__ == "__main__":
    from game.state import GameState
    
    print("Creating test game...")
    state = GameState.create_initial_state(["Alice", "Bob"], seed=42)
    
    rules = RulesEngine()
    
    print("\nGetting legal actions for Alice...")
    legal_actions = rules.get_legal_actions(state)
    
    print(f"\nFound {len(legal_actions)} legal actions:")
    for i, action in enumerate(legal_actions[:10], 1):
        print(f"  {i}. {action.get_description()}")
    
    if len(legal_actions) > 10:
        print(f"  ... and {len(legal_actions) - 10} more")
    
    # Test applying an action
    print("\nApplying first action...")
    if legal_actions:
        first_action = legal_actions[0]
        print(f"Action: {first_action.get_description()}")
        
        # Apply action
        new_state = rules.apply_action(state, first_action)
        
        print(f"\nState after action:")
        print(f"  Current player: {new_state.get_current_player().name}")
        player = new_state.get_player(0)
        print(f"  Alice's hand: {len(player.hand)} cards")
        print(f"  Alice's resources: {player.silver}S {player.gold}G {player.provisions}P")
    
    print("\nGetting legal actions for Alice...")
    legal_actions = rules.get_legal_actions(state)

    print(f"\nFound {len(legal_actions)} legal actions:")
    for i, action in enumerate(legal_actions[:10], 1):
        print(f"  {i}. {action.get_description()}")
