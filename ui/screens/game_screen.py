"""
Game screen - main game view
"""
import pygame
from game.engine import GameEngine
from game.actions import Action
from ui.config import *
from ui.views import BoardView, PlayerView, ActionPanel


class GameScreen:
    """Main game screen"""
    
    def __init__(self, screen: pygame.Surface, engine: GameEngine):
        self.screen = screen
        self.engine = engine
        self.viewing_player_idx = 0  # Which player's perspective (for card visibility)
        
        # Create views
        self.board_view = BoardView(
            BOARD_VIEW_X, BOARD_VIEW_Y,
            BOARD_VIEW_WIDTH, BOARD_VIEW_HEIGHT
        )
        
        self.player_view = PlayerView(
            PLAYER_VIEW_X, PLAYER_VIEW_Y,
            PLAYER_VIEW_WIDTH, PLAYER_VIEW_HEIGHT
        )
        
        self.action_panel = ActionPanel(
            ACTION_PANEL_X, ACTION_PANEL_Y,
            ACTION_PANEL_WIDTH, ACTION_PANEL_HEIGHT
        )
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle events
        Returns True if game should exit
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return True  # Exit to menu
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check action panel click
                legal_actions = self.engine.get_legal_actions()
                self.action_panel.handle_click(legal_actions, self._execute_action)
            
            elif event.button == 4:  # Scroll up
                legal_actions = self.engine.get_legal_actions()
                self.action_panel.handle_scroll(1, legal_actions)
            
            elif event.button == 5:  # Scroll down
                legal_actions = self.engine.get_legal_actions()
                self.action_panel.handle_scroll(-1, legal_actions)
        
        return False
    
    def _execute_action(self, action: Action):
        """Execute a game action"""
        try:
            self.engine.take_action(action)
            self.action_panel.reset_scroll()
            
            # Update viewing player to current player (for hotseat)
            self.viewing_player_idx = self.engine.state.current_player_idx
            
        except Exception as e:
            print(f"Error executing action: {e}")
    
    def update(self):
        """Update game state"""
        pass
    
    def draw(self):
        """Draw game screen"""
        self.screen.fill(DARK_GRAY)
        
        # Draw views
        self.board_view.draw(self.screen, self.engine.state)
        
        self.player_view.draw(
            self.screen,
            self.engine.state.players,
            self.engine.state.current_player_idx,
            self.viewing_player_idx
        )
        
        legal_actions = self.engine.get_legal_actions()
        self.action_panel.draw(self.screen, legal_actions, self._execute_action)
        
        # Game info overlay
        self._draw_game_info()
    
    def _draw_game_info(self):
        """Draw game information overlay"""
        info_text = f"Round {self.engine.state.round_number} | Phase: {self.engine.state.phase.value}"
        info_surface = FONT_SMALL.render(info_text, True, WHITE)
        self.screen.blit(info_surface, (WINDOW_WIDTH // 2 - 100, 5))
    
    def is_game_over(self) -> bool:
        """Check if game is over"""
        return self.engine.is_game_over()
