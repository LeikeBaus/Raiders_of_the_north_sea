"""
Game screen - main game view
"""
import pygame
from game.engine import GameEngine
from game.actions import Action
from ui import config
from ui.views import BoardView, PlayerView, ActionPanel, HistoryView, DetailView


class GameScreen:
    """Main game screen"""
    
    def __init__(self, screen: pygame.Surface, engine: GameEngine):
        self.screen = screen
        self.engine = engine
        self.viewing_player_idx = 0  # Which player's perspective (for card visibility)
        
        # Create views
        self.board_view = BoardView(
            config.BOARD_VIEW_X, config.BOARD_VIEW_Y,
            config.BOARD_VIEW_WIDTH, config.BOARD_VIEW_HEIGHT
        )
        
        self.player_view = PlayerView(
            config.PLAYER_VIEW_X, config.PLAYER_VIEW_Y,
            config.PLAYER_VIEW_WIDTH, config.PLAYER_VIEW_HEIGHT
        )
        
        self.action_panel = ActionPanel(
            config.ACTION_PANEL_X, config.ACTION_PANEL_Y,
            config.ACTION_PANEL_WIDTH, config.ACTION_PANEL_HEIGHT
        )
        
        self.history_view = HistoryView(
            config.HISTORY_PANEL_X, config.HISTORY_PANEL_Y,
            config.HISTORY_PANEL_WIDTH, config.HISTORY_PANEL_HEIGHT
        )
        
        self.detail_view = DetailView()
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle events
        Returns True if game should exit
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return True  # Exit to menu
        
        elif event.type == pygame.MOUSEMOTION:
            # Check hover for detail view
            mouse_pos = pygame.mouse.get_pos()
            self._update_hover(mouse_pos)
        
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
            # Get player info before action
            player_idx = self.engine.state.current_player_idx
            
            # Log action to history
            action_desc = self._format_action_description(action)
            self.history_view.add_entry(player_idx, action_desc)
            
            self.engine.take_action(action)
            self.action_panel.reset_scroll()
            
            # Update viewing player to current player (for hotseat)
            self.viewing_player_idx = self.engine.state.current_player_idx
            
        except Exception as e:
            print(f"Error executing action: {e}")
    
    def _update_hover(self, mouse_pos):
        """Update detail view based on mouse position"""
        # Check if hovering over board elements
        hover_info = self.board_view.get_hover_info(mouse_pos, self.engine.state)
        if hover_info:
            obj_type, obj_data = hover_info
            self.detail_view.show(mouse_pos[0] + 20, mouse_pos[1], obj_type, obj_data)
            return
        
        # Check if hovering over player cards
        hover_info = self.player_view.get_hover_info(
            mouse_pos, 
            self.engine.state.players,
            self.viewing_player_idx
        )
        if hover_info:
            obj_type, obj_data = hover_info
            self.detail_view.show(mouse_pos[0] + 20, mouse_pos[1], obj_type, obj_data)
            return
        
        # No hover
        self.detail_view.hide()
    
    def update(self):
        """Update game state"""
        pass
    
    def draw(self):
        """Draw game screen"""
        self.screen.fill(config.DARK_GRAY)
        
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
        
        # Draw history view
        self.history_view.draw(self.screen)
        
        # Game info overlay
        self._draw_game_info()
        
        # Draw detail view on top of everything
        self.detail_view.draw(self.screen)
    
    def _draw_game_info(self):
        """Draw game information overlay"""
        info_text = f"Round {self.engine.state.round_number} | Phase: {self.engine.state.phase.value}"
        info_surface = config.FONT_SMALL.render(info_text, True, config.WHITE)
        self.screen.blit(info_surface, (config.WINDOW_WIDTH // 2 - 100, 5))
    
    def _format_action_description(self, action: Action) -> str:
        """Format an action for display in history"""
        # Get action type - it's stored as action_type attribute
        if hasattr(action, 'action_type'):
            action_type = action.action_type.value if hasattr(action.action_type, 'value') else str(action.action_type)
        else:
            action_type = action.__class__.__name__
        
        # Create readable descriptions based on action type
        if action_type == "place_worker":
            # PlaceWorkerAction has building_id
            building_id = getattr(action, 'building_id', '?')
            return f"Placed worker at {building_id}"
        elif action_type == "pickup_worker":
            return "Took worker back"
        elif action_type == "play_card_town_hall":
            card_id = getattr(action, 'card_id', '?')
            return f"Played card {card_id}"
        elif action_type == "raid":
            raid_id = getattr(action, 'raid_location_id', 'raid')
            return f"Raided {raid_id}"
        elif action_type == "make_offering":
            return "Made offering"
        elif action_type == "hire_crew":
            card_id = getattr(action, 'card_id', '?')
            return f"Hired crew {card_id}"
        elif action_type == "pass_turn":
            return "Passed turn"
        else:
            return f"{action_type}"
    
    def is_game_over(self) -> bool:
        """Check if game is over"""
        return self.engine.is_game_over()
