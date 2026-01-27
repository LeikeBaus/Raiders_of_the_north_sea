"""
Game Engine for Raiders of the North Sea
Orchestrates the game loop and provides interface for agents
"""
from typing import List, Optional, Callable, Dict, Any
import copy

from game.state import GameState, PlayerState, GamePhase, WorkerColor
from game.actions import Action, PlaceWorkerAction, PickupWorkerAction, RaidAction
from game.rules import RulesEngine, get_rules_engine
from game.cards import get_card_database
from game.board import get_board_database


class GameEngine:
    """Main game engine for Raiders of the North Sea"""
    
    def __init__(self, player_names: List[str], seed: Optional[int] = None):
        """
        Initialize a new game
        
        Args:
            player_names: List of player names
            seed: Random seed for reproducibility
        """
        self.player_names = player_names
        self.seed = seed
        self.state: Optional[GameState] = None
        self.rules = get_rules_engine()
        self.action_history: List[Action] = []
        self.state_history: List[GameState] = []
        
        # Initialize the game
        self.reset()
    
    def reset(self) -> GameState:
        """Reset the game to initial state"""
        self.state = GameState.create_initial_state(self.player_names, self.seed)
        self.action_history.clear()
        self.state_history.clear()
        self.state_history.append(copy.deepcopy(self.state))
        return self.state
    
    def get_state(self) -> GameState:
        """Get current game state"""
        return self.state
    
    def get_current_player(self) -> PlayerState:
        """Get the current active player"""
        return self.state.get_current_player()
    
    def get_legal_actions(self) -> List[Action]:
        """Get all legal actions for the current player"""
        if self.is_game_over():
            return []
        return self.rules.get_legal_actions(self.state)
    
    def is_action_legal(self, action: Action) -> bool:
        """Check if an action is legal"""
        return self.rules.validate_action(self.state, action)
    
    def take_action(self, action: Action) -> GameState:
        """
        Execute an action and update game state
        
        Args:
            action: The action to execute
            
        Returns:
            Updated game state
            
        Raises:
            ValueError: If action is illegal
        """
        if not self.is_action_legal(action):
            raise ValueError(f"Illegal action: {action.get_description()}")
        
        # Execute action
        self.state = self.rules.apply_action(self.state, action)
        
        # Store in history
        self.action_history.append(action)
        self.state_history.append(copy.deepcopy(self.state))
        
        # Check for game end
        if not self.state.game_ended:
            self.rules.check_game_end(self.state)
        
        return self.state
    
    def is_game_over(self) -> bool:
        """Check if game has ended"""
        return self.state.game_ended
    
    def get_winner(self) -> Optional[PlayerState]:
        """Get the winning player (None if game not over)"""
        if not self.is_game_over():
            return None
        return self.state.get_player(self.state.winner_id)
    
    def get_scores(self) -> Dict[int, int]:
        """Get final scores for all players"""
        return {
            player.player_id: player.get_final_vp()
            for player in self.state.players
        }
    
    def get_action_history(self) -> List[Action]:
        """Get history of all actions taken"""
        return self.action_history.copy()
    
    def get_game_summary(self) -> Dict[str, Any]:
        """Get summary of game state"""
        return {
            **self.state.get_game_info(),
            "scores": self.get_scores(),
            "actions_taken": len(self.action_history),
        }
    
    def play_turn(self, agent_action_callback: Callable[[GameState, List[Action]], Action]) -> bool:
        """
        Play one turn for the current player
        
        Args:
            agent_action_callback: Function that selects an action given state and legal actions
            
        Returns:
            True if turn was played, False if game is over
        """
        if self.is_game_over():
            return False
        
        legal_actions = self.get_legal_actions()
        if not legal_actions:
            # No legal actions means game is stuck (shouldn't happen in normal play)
            return False
        
        # Let agent choose action
        chosen_action = agent_action_callback(self.state, legal_actions)
        
        # Validate and execute
        self.take_action(chosen_action)
        
        return True
    
    def play_game(self, agents: List[Callable[[GameState, List[Action]], Action]], 
                  max_turns: int = 1000, verbose: bool = False) -> GameState:
        """
        Play a complete game with given agents
        
        Args:
            agents: List of agent functions (one per player)
            max_turns: Maximum number of turns before forcing end
            verbose: Print game progress
            
        Returns:
            Final game state
        """
        if len(agents) != len(self.player_names):
            raise ValueError(f"Need {len(self.player_names)} agents, got {len(agents)}")
        
        turn_count = 0
        
        while not self.is_game_over() and turn_count < max_turns:
            current_player_idx = self.state.current_player_idx
            agent = agents[current_player_idx]
            
            if verbose:
                player = self.get_current_player()
                print(f"\n--- Turn {turn_count + 1}: {player.name} ---")
                print(f"  Hand: {len(player.hand)} cards")
                print(f"  Resources: {player.silver}S {player.gold}G {player.provisions}P")
                print(f"  Crew: {len(player.crew)}")
                print(f"  VP: {player.vp}")
            
            # Get legal actions
            legal_actions = self.get_legal_actions()
            
            if not legal_actions:
                if verbose:
                    print("  No legal actions - game may be stuck")
                break
            
            if verbose:
                print(f"  Legal actions: {len(legal_actions)}")
            
            # Let agent choose
            chosen_action = agent(self.state, legal_actions)
            
            if verbose:
                print(f"  Action: {chosen_action.get_description()}")
            
            # Execute
            self.take_action(chosen_action)
            
            turn_count += 1
        
        if verbose:
            print(f"\n{'='*50}")
            print("GAME OVER")
            print(f"{'='*50}")
            print(f"Total turns: {turn_count}")
            print(f"Total actions: {len(self.action_history)}")
            print("\nFinal Scores:")
            for player in self.state.players:
                final_vp = player.get_final_vp()
                winner_mark = " [WINNER]" if self.state.winner_id == player.player_id else ""
                print(f"  {player.name}: {final_vp} VP{winner_mark}")
                print(f"    Base VP: {player.vp}")
                print(f"    Crew VP: {sum(c.vp for c in player.crew)}")
                print(f"    Offerings VP: {sum(o.vp for o in player.offerings)}")
        
        return self.state
    
    def render_state(self) -> str:
        """Get a text representation of the current game state"""
        lines = []
        lines.append("=" * 60)
        lines.append(f"Round {self.state.round_number} - {self.state.phase.value.upper()} PHASE")
        lines.append("=" * 60)
        
        # Current player
        current = self.get_current_player()
        lines.append(f"\nCurrent Player: {current.name}")
        lines.append(f"  Worker in hand: {current.worker_in_hand.value if current.worker_in_hand else 'None'}")
        
        # All players
        lines.append("\nPlayers:")
        for player in self.state.players:
            active = "> " if player.player_id == self.state.current_player_idx else "  "
            lines.append(f"{active}{player.name}:")
            lines.append(f"    Resources: {player.silver}S {player.gold}G {player.provisions}P {player.iron}I {player.livestock}L")
            lines.append(f"    Armour: {player.armour}/10 | Valkyrie: {player.valkyrie} | VP: {player.vp}")
            lines.append(f"    Hand: {len(player.hand)} cards | Crew: {len(player.crew)} | Offerings: {len(player.offerings)}")
        
        # Game info
        lines.append(f"\nDeck: {len(self.state.townsfolk_deck)} cards")
        lines.append(f"Discard: {len(self.state.townsfolk_discard)} cards")
        lines.append(f"Offerings available: {len(self.state.visible_offerings)}")
        lines.append(f"Offerings remaining: {len(self.state.offering_stack)}")
        
        # Worker placements
        lines.append(f"\nWorkers on buildings: {len(self.state.worker_placements)}")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)


def create_random_agent() -> Callable[[GameState, List[Action]], Action]:
    """Create a simple random agent"""
    import random
    
    def random_agent(state: GameState, legal_actions: List[Action]) -> Action:
        """Select a random legal action"""
        return random.choice(legal_actions)
    
    return random_agent


def create_greedy_agent() -> Callable[[GameState, List[Action]], Action]:
    """Create a simple greedy agent (prefers pickup over place, raids over work)"""
    
    def greedy_agent(state: GameState, legal_actions: List[Action]) -> Action:
        """Select action greedily"""
        import random
        
        # Prefer raids if available
        raids = [a for a in legal_actions if isinstance(a, RaidAction)]
        if raids:
            return random.choice(raids)
        
        # Prefer pickup actions (ends turn and gets resources)
        pickups = [a for a in legal_actions if isinstance(a, PickupWorkerAction)]
        if pickups:
            return random.choice(pickups)
        
        # Otherwise place worker
        return random.choice(legal_actions)
    
    return greedy_agent


if __name__ == "__main__":
    print("Testing Game Engine...")
    
    # Create a game
    engine = GameEngine(["Alice", "Bob", "Charlie"], seed=42)
    
    print("\nInitial State:")
    print(engine.render_state())
    
    print(f"\nLegal actions for {engine.get_current_player().name}:")
    legal = engine.get_legal_actions()
    for i, action in enumerate(legal[:5], 1):
        print(f"  {i}. {action.get_description()}")
    if len(legal) > 5:
        print(f"  ... and {len(legal) - 5} more")
    
    # Play a few turns manually
    print("\n" + "="*60)
    print("Playing 5 actions...")
    print("="*60)
    
    for i in range(5):
        legal = engine.get_legal_actions()
        if not legal:
            break
        
        import random
        action = random.choice(legal)
        print(f"\nAction {i+1}: {action.get_description()}")
        engine.take_action(action)
        print(f"  Current player after action: {engine.get_current_player().name}")
    
    print("\n" + "="*60)
    print("Testing full game with random agents...")
    print("="*60)
    
    # Reset and play full game
    engine.reset()
    agents = [create_random_agent() for _ in range(3)]
    
    final_state = engine.play_game(agents, verbose=True, max_turns=10)
    
    print("\nGame Summary:")
    print(engine.get_game_summary())
