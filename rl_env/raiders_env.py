"""
Gymnasium Environment for Raiders of the North Sea
Provides RL-compatible interface for training agents
"""
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from typing import Dict, Any, Tuple, Optional, List
import copy

from game.engine import GameEngine
from game.state import GameState, PlayerState
from game.actions import Action, ActionType


class RaidersEnv(gym.Env):
    """
    Gymnasium environment for Raiders of the North Sea
    
    Supports:
    - 2-4 players
    - Self-play training
    - Legal action masking
    - Configurable reward shaping
    """
    
    metadata = {'render_modes': ['human', 'ansi'], 'render_fps': 1}
    
    def __init__(
        self,
        num_players: int = 2,
        reward_shaping: str = 'sparse',
        max_turns: int = 500,
        render_mode: Optional[str] = None,
        seed: Optional[int] = None
    ):
        """
        Initialize environment
        
        Args:
            num_players: Number of players (2-4)
            reward_shaping: 'sparse' (final VP only) or 'dense' (intermediate rewards)
            max_turns: Maximum turns before truncation
            render_mode: 'human' or 'ansi'
            seed: Random seed
        """
        super().__init__()
        
        if not 2 <= num_players <= 4:
            raise ValueError("num_players must be between 2 and 4")
        
        self.num_players = num_players
        self.reward_shaping = reward_shaping
        self.max_turns = max_turns
        self.render_mode = render_mode
        self.seed_value = seed
        
        # Create player names
        player_names = [f"Player{i}" for i in range(num_players)]
        
        # Initialize game engine
        self.engine = GameEngine(player_names, seed=seed)
        
        # Maximum possible actions (estimate upper bound)
        # PlaceWorker: ~8 buildings, PickupWorker: ~8 buildings,
        # HireCrew: ~8 cards, TownHall: ~8 cards, Raid: ~10 locations * ~5 crew combos
        self.max_actions = 200
        
        # Define observation and action spaces
        self._define_spaces()
        
        # Track rewards for shaping
        self.previous_vp = [0] * num_players
        self.turn_count = 0
    
    def _define_spaces(self):
        """Define observation and action spaces"""
        
        # Observation space: flattened game state
        # Features per player: resources (5), armour, valkyrie, vp, hand_size, crew_count, offering_count
        # Features global: deck_size, discard_size, offerings_available, round_number, current_player
        # Worker placements: simplified board state
        
        obs_dim = (
            self.num_players * 12 +  # Per-player features
            20 +  # Global features
            50   # Board state (worker placements, raid states)
        )
        
        self.observation_space = spaces.Dict({
            'observation': spaces.Box(
                low=-10.0,
                high=100.0,
                shape=(obs_dim,),
                dtype=np.float32
            ),
            'action_mask': spaces.Box(
                low=0,
                high=1,
                shape=(self.max_actions,),
                dtype=np.int8
            )
        })
        
        # Action space: discrete actions
        self.action_space = spaces.Discrete(self.max_actions)
    
    def reset(
        self,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, np.ndarray], Dict[str, Any]]:
        """
        Reset environment to initial state
        
        Returns:
            observation: Dict with 'observation' and 'action_mask'
            info: Additional information
        """
        if seed is not None:
            self.seed_value = seed
        
        # Reset game
        self.engine.reset()
        self.turn_count = 0
        self.previous_vp = [0] * self.num_players
        
        # Get initial observation
        obs = self._get_observation()
        info = self._get_info()
        
        return obs, info
    
    def step(
        self,
        action_id: int
    ) -> Tuple[Dict[str, np.ndarray], float, bool, bool, Dict[str, Any]]:
        """
        Execute action and return result
        
        Args:
            action_id: Discrete action ID
            
        Returns:
            observation: New observation
            reward: Reward for current player
            terminated: Whether game ended naturally
            truncated: Whether game was truncated (max turns)
            info: Additional information
        """
        # Get current player before action
        current_player_id = self.engine.state.current_player_idx
        
        # Map action ID to game action
        action = self._action_id_to_game_action(action_id)
        
        if action is None:
            # Invalid action - penalize
            obs = self._get_observation()
            reward = -1.0
            terminated = False
            truncated = False
            info = self._get_info()
            info['invalid_action'] = True
            return obs, reward, terminated, truncated, info
        
        # Execute action
        try:
            self.engine.take_action(action)
            self.turn_count += 1
        except ValueError as e:
            # Action was illegal - penalize
            obs = self._get_observation()
            reward = -1.0
            terminated = False
            truncated = False
            info = self._get_info()
            info['illegal_action'] = str(e)
            return obs, reward, terminated, truncated, info
        
        # Calculate reward
        reward = self._calculate_reward(current_player_id)
        
        # Check termination
        terminated = self.engine.is_game_over()
        truncated = self.turn_count >= self.max_turns
        
        # Get new observation
        obs = self._get_observation()
        info = self._get_info()
        
        return obs, reward, terminated, truncated, info
    
    def _get_observation(self) -> Dict[str, np.ndarray]:
        """
        Convert game state to observation
        
        Returns:
            Dict with 'observation' (state vector) and 'action_mask' (legal actions)
        """
        state = self.engine.state
        
        # Build observation vector
        obs_parts = []
        
        # Per-player features (normalized)
        for player in state.players:
            obs_parts.extend([
                player.silver / 20.0,      # Normalize to ~[0, 1]
                player.gold / 10.0,
                player.provisions / 10.0,
                player.iron / 10.0,
                player.livestock / 10.0,
                player.armour / 10.0,
                player.valkyrie / 5.0,
                player.vp / 50.0,
                len(player.hand) / 8.0,
                len(player.crew) / 5.0,
                len(player.offerings) / 5.0,
                1.0 if player.worker_in_hand else 0.0,
            ])
        
        # Pad if fewer than 4 players
        for _ in range(4 - self.num_players):
            obs_parts.extend([0.0] * 12)
        
        # Global features
        # Calculate valkyrie pool from GameState
        total_valkyrie = state.valkyrie_pool if hasattr(state, 'valkyrie_pool') else 18
        
        obs_parts.extend([
            len(state.townsfolk_deck) / 71.0,
            len(state.townsfolk_discard) / 71.0,
            len(state.visible_offerings) / 4.0,
            len(state.offering_stack) / 16.0,
            state.round_number / 10.0,
            state.current_player_idx / self.num_players,
            1.0 if state.game_ended else 0.0,
            total_valkyrie / 18.0,
        ])
        
        # Additional global features
        obs_parts.extend([0.0] * 12)  # Reserved for future use
        
        # Board state: worker placements
        building_workers = [0.0] * 8  # 8 buildings
        for placement in state.worker_placements:
            # Count workers per building (simplified)
            building_id = placement.building_id
            # Map building_id to index (simplified - just use hash)
            idx = abs(hash(building_id)) % 8
            building_workers[idx] += 1.0
        obs_parts.extend([w / 4.0 for w in building_workers])  # Normalize
        
        # Raid states
        raid_plunder = []
        for raid_state in state.raid_states:
            raid_plunder.append(raid_state.plunder_remaining / 10.0)
        # Pad to 23 sublocations
        while len(raid_plunder) < 23:
            raid_plunder.append(0.0)
        obs_parts.extend(raid_plunder[:23])
        
        # Additional board state
        obs_parts.extend([0.0] * 19)  # Reserved
        
        # Create observation array
        observation = np.array(obs_parts, dtype=np.float32)
        
        # Get legal action mask
        action_mask = self._get_action_mask()
        
        return {
            'observation': observation,
            'action_mask': action_mask
        }
    
    def _get_action_mask(self) -> np.ndarray:
        """
        Get mask of legal actions (1 = legal, 0 = illegal)
        
        Returns:
            Binary mask of shape (max_actions,)
        """
        mask = np.zeros(self.max_actions, dtype=np.int8)
        
        # Get legal actions from engine
        legal_actions = self.engine.get_legal_actions()
        
        # Map each legal action to its ID
        for action in legal_actions:
            action_id = self._game_action_to_action_id(action)
            if 0 <= action_id < self.max_actions:
                mask[action_id] = 1
        
        return mask
    
    def _game_action_to_action_id(self, action: Action) -> int:
        """
        Map game action to discrete action ID
        
        Action ID encoding:
        0-7: PlaceWorker at building 0-7
        8-15: PickupWorker from building 0-7
        16-50: HireCrew (card indices)
        51-85: PlayCardTownHall (card indices)
        86-185: Raid actions (location * crew combinations)
        186-199: Reserved
        
        Returns:
            Action ID (0 to max_actions-1)
        """
        from game.actions import PlaceWorkerAction, PickupWorkerAction, HireCrewAction, PlayCardTownHallAction, RaidAction
        from game.board import get_board_database
        
        if isinstance(action, PlaceWorkerAction):
            # Map building_id to index
            board_db = get_board_database()
            building_idx = self._building_to_index(action.building_id)
            return building_idx  # 0-7
        
        elif isinstance(action, PickupWorkerAction):
            building_idx = self._building_to_index(action.building_id)
            return 8 + building_idx  # 8-15
        
        elif isinstance(action, HireCrewAction):
            # Use card hash for indexing
            card_idx = abs(hash(action.card_id)) % 35
            return 16 + card_idx  # 16-50
        
        elif isinstance(action, PlayCardTownHallAction):
            card_idx = abs(hash(action.card_id)) % 35
            return 51 + card_idx  # 51-85
        
        elif isinstance(action, RaidAction):
            location_idx = abs(hash(action.location_id)) % 10
            crew_hash = abs(hash(tuple(sorted(action.crew_ids)))) % 10
            return 86 + location_idx * 10 + crew_hash  # 86-185
        
        return 0  # Default
    
    def _action_id_to_game_action(self, action_id: int) -> Optional[Action]:
        """
        Map discrete action ID to game action
        
        Returns:
            Game action or None if invalid
        """
        # Get legal actions
        legal_actions = self.engine.get_legal_actions()
        
        if not legal_actions:
            return None
        
        # Find action matching this ID
        for action in legal_actions:
            if self._game_action_to_action_id(action) == action_id:
                return action
        
        # If no exact match, try to find closest legal action of same type
        action_type = self._action_id_to_type(action_id)
        type_matches = [a for a in legal_actions if self._get_action_type(a) == action_type]
        
        if type_matches:
            return type_matches[0]
        
        # Fall back to first legal action
        return legal_actions[0] if legal_actions else None
    
    def _action_id_to_type(self, action_id: int) -> str:
        """Get action type from action ID"""
        if 0 <= action_id < 8:
            return 'place'
        elif 8 <= action_id < 16:
            return 'pickup'
        elif 16 <= action_id < 51:
            return 'hire'
        elif 51 <= action_id < 86:
            return 'townhall'
        elif 86 <= action_id < 186:
            return 'raid'
        return 'unknown'
    
    def _get_action_type(self, action: Action) -> str:
        """Get action type string"""
        from game.actions import PlaceWorkerAction, PickupWorkerAction, HireCrewAction, PlayCardTownHallAction, RaidAction
        
        if isinstance(action, PlaceWorkerAction):
            return 'place'
        elif isinstance(action, PickupWorkerAction):
            return 'pickup'
        elif isinstance(action, HireCrewAction):
            return 'hire'
        elif isinstance(action, PlayCardTownHallAction):
            return 'townhall'
        elif isinstance(action, RaidAction):
            return 'raid'
        return 'unknown'
    
    def _building_to_index(self, building_id: str) -> int:
        """Map building ID to index 0-7"""
        buildings = ['gate_house', 'town_hall', 'treasury', 'barracks', 'armoury', 'mill', 'silversmith', 'long_house']
        try:
            return buildings.index(building_id)
        except ValueError:
            return abs(hash(building_id)) % 8
    
    def _calculate_reward(self, player_id: int) -> float:
        """
        Calculate reward for player
        
        Args:
            player_id: Player who took action
            
        Returns:
            Reward value
        """
        player = self.engine.state.get_player(player_id)
        
        if self.reward_shaping == 'sparse':
            # Only reward at game end
            if self.engine.is_game_over():
                final_vp = player.get_final_vp()
                # Normalize to [-1, 1] range, 1 for winner
                if self.engine.state.winner_id == player_id:
                    return 1.0
                else:
                    # Scale by how close to winner
                    winner = self.engine.get_winner()
                    winner_vp = winner.get_final_vp() if winner else final_vp
                    return (final_vp / max(winner_vp, 1)) - 1.0
            return 0.0
        
        else:  # dense rewards
            # Reward VP gains
            current_vp = player.vp
            vp_gain = current_vp - self.previous_vp[player_id]
            self.previous_vp[player_id] = current_vp
            
            # Small rewards for good actions
            reward = vp_gain * 0.1
            
            # Bonus for hiring crew
            reward += len(player.crew) * 0.01
            
            # Bonus for offerings
            reward += len(player.offerings) * 0.02
            
            # Large reward for winning
            if self.engine.is_game_over():
                if self.engine.state.winner_id == player_id:
                    reward += 1.0
                else:
                    reward -= 0.5
            
            return reward
    
    def _get_info(self) -> Dict[str, Any]:
        """Get additional info"""
        state = self.engine.state
        current_player = self.engine.get_current_player()
        
        return {
            'current_player': state.current_player_idx,
            'round': state.round_number,
            'turn_count': self.turn_count,
            'game_over': self.engine.is_game_over(),
            'legal_actions_count': len(self.engine.get_legal_actions()),
            'player_vp': current_player.vp,
            'player_crew': len(current_player.crew),
        }
    
    def render(self):
        """Render the environment"""
        if self.render_mode == 'human' or self.render_mode == 'ansi':
            return self.engine.render_state()
        return None
    
    def close(self):
        """Clean up resources"""
        pass


def make_env(num_players: int = 2, **kwargs) -> RaidersEnv:
    """
    Factory function to create environment
    
    Args:
        num_players: Number of players
        **kwargs: Additional arguments for RaidersEnv
        
    Returns:
        Configured environment
    """
    return RaidersEnv(num_players=num_players, **kwargs)


if __name__ == "__main__":
    print("Testing RaidersEnv...")
    
    # Create environment
    env = RaidersEnv(num_players=2, reward_shaping='dense', render_mode='human')
    
    print("\nObservation space:", env.observation_space)
    print("Action space:", env.action_space)
    
    # Reset
    obs, info = env.reset(seed=42)
    print("\nInitial observation shape:", obs['observation'].shape)
    print("Action mask sum (legal actions):", obs['action_mask'].sum())
    print("Info:", info)
    
    # Take random actions
    print("\n" + "="*60)
    print("Taking 10 random legal actions...")
    print("="*60)
    
    for i in range(10):
        # Get legal actions
        legal_mask = obs['action_mask']
        legal_action_ids = np.where(legal_mask == 1)[0]
        
        if len(legal_action_ids) == 0:
            print("No legal actions!")
            break
        
        # Sample random legal action
        action_id = np.random.choice(legal_action_ids)
        
        print(f"\nStep {i+1}:")
        print(f"  Action ID: {action_id}")
        print(f"  Legal actions: {len(legal_action_ids)}")
        
        # Take step
        obs, reward, terminated, truncated, info = env.step(action_id)
        
        print(f"  Reward: {reward:.3f}")
        print(f"  Player VP: {info['player_vp']}")
        print(f"  Terminated: {terminated}, Truncated: {truncated}")
        
        if terminated or truncated:
            print("\nGame ended!")
            break
    
    print("\n" + "="*60)
    print("Environment test complete!")
    print("="*60)
