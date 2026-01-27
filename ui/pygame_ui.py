"""
Pygame-based UI for Raiders of the North Sea
Simple interface for human players
"""
import pygame
import sys
from typing import List, Optional, Callable, Tuple
from enum import Enum

from game.engine import GameEngine, create_random_agent
from game.state import GameState, PlayerState
from game.actions import Action, PlaceWorkerAction, PickupWorkerAction, HireCrewAction, PlayCardTownHallAction, RaidAction


class UIState(Enum):
    """UI state machine"""
    MENU = "menu"
    GAME = "game"
    ACTION_SELECT = "action_select"
    GAME_OVER = "game_over"


class RaidersUI:
    """Main UI class for Raiders of the North Sea"""
    
    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (200, 200, 200)
    DARK_GRAY = (64, 64, 64)
    RED = (220, 50, 50)
    GREEN = (50, 200, 50)
    BLUE = (50, 100, 200)
    YELLOW = (255, 200, 50)
    BROWN = (139, 69, 19)
    GOLD = (255, 215, 0)
    
    # Window settings
    WINDOW_WIDTH = 1400
    WINDOW_HEIGHT = 900
    FPS = 60
    
    def __init__(self):
        """Initialize pygame and UI"""
        pygame.init()
        
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Raiders of the North Sea")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 18)
        
        # Game state
        self.ui_state = UIState.MENU
        self.engine: Optional[GameEngine] = None
        self.selected_action_idx: Optional[int] = None
        self.scroll_offset = 0
        
        # Menu state
        self.num_players = 2
        self.player_types = [True, True]  # True = Human, False = AI
        
        # Action list scrolling
        self.actions_per_page = 15
        
    def run(self):
        """Main game loop"""
        while self.running:
            self._handle_events()
            self._update()
            self._render()
            self.clock.tick(self.FPS)
        
        pygame.quit()
        sys.exit()
    
    def _handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self._handle_click(event.pos)
                elif event.button == 4:  # Scroll up
                    self.scroll_offset = max(0, self.scroll_offset - 1)
                elif event.button == 5:  # Scroll down
                    if self.engine:
                        legal_actions = self.engine.get_legal_actions()
                        max_scroll = max(0, len(legal_actions) - self.actions_per_page)
                        self.scroll_offset = min(max_scroll, self.scroll_offset + 1)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.ui_state == UIState.GAME:
                        self.ui_state = UIState.MENU
                        self.engine = None
    
    def _handle_click(self, pos: Tuple[int, int]):
        """Handle mouse clicks"""
        x, y = pos
        
        if self.ui_state == UIState.MENU:
            self._handle_menu_click(x, y)
        elif self.ui_state == UIState.GAME:
            self._handle_game_click(x, y)
        elif self.ui_state == UIState.GAME_OVER:
            self._handle_game_over_click(x, y)
    
    def _handle_menu_click(self, x: int, y: int):
        """Handle clicks in menu"""
        # Player count buttons (2-4 players)
        button_y = 250
        for i in range(2, 5):
            button_x = 500 + (i - 2) * 120
            if button_x <= x <= button_x + 100 and button_y <= y <= button_y + 50:
                self.num_players = i
                self.player_types = [True] * i
        
        # Start game button
        if 600 <= x <= 800 and 500 <= y <= 570:
            self._start_game()
    
    def _handle_game_click(self, x: int, y: int):
        """Handle clicks during game"""
        # Check if clicking on action list
        actions_x = 950
        actions_y = 100
        action_height = 35
        
        if actions_x <= x <= self.WINDOW_WIDTH - 20:
            legal_actions = self.engine.get_legal_actions()
            visible_actions = legal_actions[self.scroll_offset:self.scroll_offset + self.actions_per_page]
            
            for i, action in enumerate(visible_actions):
                button_y = actions_y + i * action_height
                if button_y <= y <= button_y + 30:
                    # Execute this action
                    actual_idx = i + self.scroll_offset
                    if actual_idx < len(legal_actions):
                        self._execute_action(legal_actions[actual_idx])
                    break
    
    def _handle_game_over_click(self, x: int, y: int):
        """Handle clicks on game over screen"""
        # Back to menu button
        if 550 <= x <= 850 and 700 <= y <= 770:
            self.ui_state = UIState.MENU
            self.engine = None
    
    def _start_game(self):
        """Start a new game"""
        player_names = [f"Player {i+1}" for i in range(self.num_players)]
        self.engine = GameEngine(player_names, seed=None)
        self.ui_state = UIState.GAME
        self.scroll_offset = 0
    
    def _execute_action(self, action: Action):
        """Execute a game action"""
        try:
            self.engine.take_action(action)
            self.scroll_offset = 0
            
            # Check if game is over
            if self.engine.is_game_over():
                self.ui_state = UIState.GAME_OVER
        except Exception as e:
            print(f"Error executing action: {e}")
    
    def _update(self):
        """Update game state"""
        pass
    
    def _render(self):
        """Render current state"""
        self.screen.fill(self.WHITE)
        
        if self.ui_state == UIState.MENU:
            self._render_menu()
        elif self.ui_state == UIState.GAME:
            self._render_game()
        elif self.ui_state == UIState.GAME_OVER:
            self._render_game_over()
        
        pygame.display.flip()
    
    def _render_menu(self):
        """Render main menu"""
        # Title
        title = self.font_large.render("Raiders of the North Sea", True, self.BLACK)
        title_rect = title.get_rect(center=(self.WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Player count selection
        subtitle = self.font_medium.render("Select Number of Players:", True, self.BLACK)
        subtitle_rect = subtitle.get_rect(center=(self.WINDOW_WIDTH // 2, 200))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Player count buttons
        for i in range(2, 5):
            button_x = 500 + (i - 2) * 120
            button_y = 250
            color = self.GREEN if self.num_players == i else self.LIGHT_GRAY
            pygame.draw.rect(self.screen, color, (button_x, button_y, 100, 50))
            pygame.draw.rect(self.screen, self.BLACK, (button_x, button_y, 100, 50), 2)
            
            text = self.font_medium.render(str(i), True, self.BLACK)
            text_rect = text.get_rect(center=(button_x + 50, button_y + 25))
            self.screen.blit(text, text_rect)
        
        # Player info
        info_y = 350
        for i in range(self.num_players):
            player_text = self.font_small.render(f"Player {i+1}: Human", True, self.BLACK)
            player_rect = player_text.get_rect(center=(self.WINDOW_WIDTH // 2, info_y + i * 30))
            self.screen.blit(player_text, player_rect)
        
        # Start button
        button_rect = pygame.Rect(600, 500, 200, 70)
        pygame.draw.rect(self.screen, self.GREEN, button_rect)
        pygame.draw.rect(self.screen, self.BLACK, button_rect, 3)
        
        start_text = self.font_medium.render("Start Game", True, self.BLACK)
        start_rect = start_text.get_rect(center=button_rect.center)
        self.screen.blit(start_text, start_rect)
        
        # Instructions
        instructions = [
            "Click on actions in the right panel to play",
            "ESC to return to menu"
        ]
        for i, instruction in enumerate(instructions):
            text = self.font_tiny.render(instruction, True, self.GRAY)
            text_rect = text.get_rect(center=(self.WINDOW_WIDTH // 2, 650 + i * 25))
            self.screen.blit(text, text_rect)
    
    def _render_game(self):
        """Render game state"""
        if not self.engine:
            return
        
        state = self.engine.state
        current_player = self.engine.get_current_player()
        
        # Left panel: Game info and player states
        self._render_game_info(state, current_player)
        
        # Right panel: Legal actions
        self._render_actions_panel()
    
    def _render_game_info(self, state: GameState, current_player: PlayerState):
        """Render game information and player states"""
        panel_width = 930
        
        # Background
        pygame.draw.rect(self.screen, self.LIGHT_GRAY, (0, 0, panel_width, self.WINDOW_HEIGHT))
        pygame.draw.line(self.screen, self.BLACK, (panel_width, 0), (panel_width, self.WINDOW_HEIGHT), 3)
        
        # Game header
        header_y = 20
        round_text = self.font_medium.render(f"Round {state.round_number}", True, self.BLACK)
        self.screen.blit(round_text, (20, header_y))
        
        phase_text = self.font_small.render(f"Phase: {state.phase.value}", True, self.DARK_GRAY)
        self.screen.blit(phase_text, (20, header_y + 35))
        
        # Deck info
        deck_text = self.font_tiny.render(f"Deck: {len(state.townsfolk_deck)} | Discard: {len(state.townsfolk_discard)}", True, self.DARK_GRAY)
        self.screen.blit(deck_text, (20, header_y + 60))
        
        # Current player highlight
        current_text = self.font_medium.render(f"Current: {current_player.name}", True, self.RED)
        self.screen.blit(current_text, (400, header_y))
        
        # Player states
        player_y = 120
        for i, player in enumerate(state.players):
            self._render_player_state(player, 20, player_y + i * 180, player == current_player)
    
    def _render_player_state(self, player: PlayerState, x: int, y: int, is_current: bool):
        """Render a player's state"""
        panel_width = 890
        panel_height = 170
        
        # Background
        bg_color = self.YELLOW if is_current else self.WHITE
        pygame.draw.rect(self.screen, bg_color, (x, y, panel_width, panel_height))
        pygame.draw.rect(self.screen, self.BLACK, (x, y, panel_width, panel_height), 2)
        
        # Player name and VP
        name_text = self.font_medium.render(f"{player.name} - {player.vp} VP", True, self.BLACK)
        self.screen.blit(name_text, (x + 10, y + 10))
        
        # Worker in hand
        worker_text = self.font_small.render(
            f"Worker: {player.worker_in_hand.value if player.worker_in_hand else 'None'}",
            True, self.BLACK
        )
        self.screen.blit(worker_text, (x + 10, y + 45))
        
        # Resources
        resources_y = y + 75
        resources = [
            (f"Silver: {player.silver}", self.LIGHT_GRAY),
            (f"Gold: {player.gold}", self.GOLD),
            (f"Prov: {player.provisions}", self.BROWN),
            (f"Iron: {player.iron}", self.DARK_GRAY),
            (f"Livestock: {player.livestock}", self.GREEN),
        ]
        
        for i, (text, color) in enumerate(resources):
            resource_text = self.font_tiny.render(text, True, self.BLACK)
            bg_rect = pygame.Rect(x + 10 + i * 100, resources_y, 90, 25)
            pygame.draw.rect(self.screen, color, bg_rect)
            pygame.draw.rect(self.screen, self.BLACK, bg_rect, 1)
            text_rect = resource_text.get_rect(center=bg_rect.center)
            self.screen.blit(resource_text, text_rect)
        
        # Combat stats
        stats_y = resources_y + 35
        stats_text = self.font_tiny.render(
            f"Armour: {player.armour} | Valkyrie: {player.valkyrie}",
            True, self.BLACK
        )
        self.screen.blit(stats_text, (x + 10, stats_y))
        
        # Cards and crew
        cards_y = stats_y + 25
        cards_text = self.font_tiny.render(
            f"Hand: {len(player.hand)} cards | Crew: {len(player.crew)} | Offerings: {len(player.offerings)}",
            True, self.BLACK
        )
        self.screen.blit(cards_text, (x + 10, cards_y))
        
        # Show hand (card names)
        if player.hand:
            hand_y = cards_y + 25
            hand_names = ", ".join([c.name[:15] for c in player.hand[:5]])
            if len(player.hand) > 5:
                hand_names += f" +{len(player.hand)-5} more"
            hand_text = self.font_tiny.render(f"Cards: {hand_names}", True, self.DARK_GRAY)
            self.screen.blit(hand_text, (x + 10, hand_y))
    
    def _render_actions_panel(self):
        """Render legal actions panel"""
        panel_x = 950
        panel_width = self.WINDOW_WIDTH - panel_x - 20
        
        # Header
        header_text = self.font_medium.render("Legal Actions", True, self.BLACK)
        self.screen.blit(header_text, (panel_x, 20))
        
        # Instructions
        instruction_text = self.font_tiny.render("Click to execute action", True, self.GRAY)
        self.screen.blit(instruction_text, (panel_x, 55))
        
        scroll_text = self.font_tiny.render("Scroll: Mouse wheel", True, self.GRAY)
        self.screen.blit(scroll_text, (panel_x, 75))
        
        # Get legal actions
        legal_actions = self.engine.get_legal_actions()
        
        if not legal_actions:
            no_actions_text = self.font_small.render("No legal actions!", True, self.RED)
            self.screen.blit(no_actions_text, (panel_x, 120))
            return
        
        # Show scrollable list of actions
        visible_actions = legal_actions[self.scroll_offset:self.scroll_offset + self.actions_per_page]
        
        action_y = 100
        action_height = 35
        
        for i, action in enumerate(visible_actions):
            button_y = action_y + i * action_height
            button_rect = pygame.Rect(panel_x, button_y, panel_width, 30)
            
            # Hover effect
            mouse_pos = pygame.mouse.get_pos()
            is_hover = button_rect.collidepoint(mouse_pos)
            color = self.GREEN if is_hover else self.LIGHT_GRAY
            
            pygame.draw.rect(self.screen, color, button_rect)
            pygame.draw.rect(self.screen, self.BLACK, button_rect, 1)
            
            # Action text
            action_text = self._get_action_text(action)
            text_surface = self.font_tiny.render(action_text, True, self.BLACK)
            self.screen.blit(text_surface, (panel_x + 5, button_y + 7))
        
        # Scroll indicator
        if len(legal_actions) > self.actions_per_page:
            scroll_info = self.font_tiny.render(
                f"{self.scroll_offset + 1}-{min(self.scroll_offset + self.actions_per_page, len(legal_actions))} of {len(legal_actions)}",
                True, self.GRAY
            )
            self.screen.blit(scroll_info, (panel_x, action_y + self.actions_per_page * action_height + 10))
    
    def _get_action_text(self, action: Action) -> str:
        """Get readable text for action"""
        from game.actions import PlaceWorkerAction, PickupWorkerAction, HireCrewAction, PlayCardTownHallAction, RaidAction
        
        if isinstance(action, PlaceWorkerAction):
            return f"Place at {action.building_id}"
        elif isinstance(action, PickupWorkerAction):
            return f"Pickup from {action.building_id}"
        elif isinstance(action, HireCrewAction):
            return f"Hire: {action.card_id}"
        elif isinstance(action, PlayCardTownHallAction):
            return f"Town Hall: {action.card_id}"
        elif isinstance(action, RaidAction):
            return f"Raid {action.location_id}/{action.sublocation_id} ({len(action.crew_ids)} crew)"
        else:
            return action.get_description()
    
    def _render_game_over(self):
        """Render game over screen"""
        if not self.engine:
            return
        
        # Title
        title = self.font_large.render("Game Over!", True, self.BLACK)
        title_rect = title.get_rect(center=(self.WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Winner
        winner = self.engine.get_winner()
        if winner:
            winner_text = self.font_medium.render(f"Winner: {winner.name}", True, self.GREEN)
            winner_rect = winner_text.get_rect(center=(self.WINDOW_WIDTH // 2, 200))
            self.screen.blit(winner_text, winner_rect)
        
        # Scores
        scores = self.engine.get_scores()
        scores_y = 300
        
        scores_title = self.font_medium.render("Final Scores:", True, self.BLACK)
        scores_title_rect = scores_title.get_rect(center=(self.WINDOW_WIDTH // 2, scores_y))
        self.screen.blit(scores_title, scores_title_rect)
        
        sorted_players = sorted(self.engine.state.players, key=lambda p: p.get_final_vp(), reverse=True)
        
        for i, player in enumerate(sorted_players):
            score_text = self.font_small.render(
                f"{i+1}. {player.name}: {player.get_final_vp()} VP",
                True, self.BLACK
            )
            score_rect = score_text.get_rect(center=(self.WINDOW_WIDTH // 2, scores_y + 50 + i * 40))
            self.screen.blit(score_text, score_rect)
        
        # Summary
        summary_y = scores_y + 50 + len(sorted_players) * 40 + 50
        summary = self.engine.get_game_summary()
        summary_text = self.font_small.render(
            f"Rounds: {summary['round']} | Actions: {summary['actions_taken']}",
            True, self.DARK_GRAY
        )
        summary_rect = summary_text.get_rect(center=(self.WINDOW_WIDTH // 2, summary_y))
        self.screen.blit(summary_text, summary_rect)
        
        # Back to menu button
        button_rect = pygame.Rect(550, 700, 300, 70)
        pygame.draw.rect(self.screen, self.BLUE, button_rect)
        pygame.draw.rect(self.screen, self.BLACK, button_rect, 3)
        
        menu_text = self.font_medium.render("Back to Menu", True, self.WHITE)
        menu_rect = menu_text.get_rect(center=button_rect.center)
        self.screen.blit(menu_text, menu_rect)


def main():
    """Main entry point"""
    ui = RaidersUI()
    ui.run()


if __name__ == "__main__":
    main()
