"""
Main UI Entry Point - Game Loop
"""
import pygame
import sys
from enum import Enum

from game.engine import GameEngine
from ui import config
from ui.screens import MenuScreen, GameScreen, GameOverScreen


class GameState(Enum):
    """UI state machine"""
    MENU = "menu"
    PLAYING = "playing"
    GAME_OVER = "game_over"


class RaidersUI:
    """Main UI application"""
    
    def __init__(self):
        """Initialize pygame and UI"""
        pygame.init()
        
        # Create window
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        pygame.display.set_caption(config.TITLE)
        
        # Clock for FPS
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize fonts
        config.init_fonts()
        
        # UI state
        self.state = GameState.MENU
        self.engine = None
        
        # Screens
        self.menu_screen = MenuScreen(self.screen)
        self.game_screen = None
        self.game_over_screen = None
    
    def run(self):
        """Main game loop"""
        while self.running:
            self._handle_events()
            self._update()
            self._render()
            self.clock.tick(config.FPS)
        
        pygame.quit()
        sys.exit()
    
    def _handle_events(self):
        """Handle all pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif self.state == GameState.MENU:
                self.menu_screen.handle_event(event, self._start_game)
            
            elif self.state == GameState.PLAYING:
                if self.game_screen:
                    exit_game = self.game_screen.handle_event(event)
                    if exit_game:
                        self._return_to_menu()
            
            elif self.state == GameState.GAME_OVER:
                if self.game_over_screen:
                    self.game_over_screen.handle_event(event, self._return_to_menu)
    
    def _update(self):
        """Update current screen"""
        if self.state == GameState.MENU:
            self.menu_screen.update()
        
        elif self.state == GameState.PLAYING:
            if self.game_screen:
                self.game_screen.update()
                
                # Check if game ended
                if self.game_screen.is_game_over():
                    self._show_game_over()
        
        elif self.state == GameState.GAME_OVER:
            if self.game_over_screen:
                self.game_over_screen.update()
    
    def _render(self):
        """Render current screen"""
        if self.state == GameState.MENU:
            self.menu_screen.draw()
        
        elif self.state == GameState.PLAYING:
            if self.game_screen:
                self.game_screen.draw()
        
        elif self.state == GameState.GAME_OVER:
            if self.game_over_screen:
                self.game_over_screen.draw()
        
        pygame.display.flip()
    
    def _start_game(self, num_players: int, player_types: list):
        """Start a new game"""
        # Create player names
        player_names = [f"Player {i+1}" for i in range(num_players)]
        
        # Create game engine
        self.engine = GameEngine(player_names, seed=None)
        
        # Create game screen
        self.game_screen = GameScreen(self.screen, self.engine)
        
        # Switch to playing state
        self.state = GameState.PLAYING
    
    def _show_game_over(self):
        """Show game over screen"""
        self.game_over_screen = GameOverScreen(self.screen, self.engine)
        self.state = GameState.GAME_OVER
    
    def _return_to_menu(self):
        """Return to main menu"""
        self.state = GameState.MENU
        self.engine = None
        self.game_screen = None
        self.game_over_screen = None
        self.menu_screen = MenuScreen(self.screen)


def main():
    """Main entry point"""
    ui = RaidersUI()
    ui.run()


if __name__ == "__main__":
    main()
