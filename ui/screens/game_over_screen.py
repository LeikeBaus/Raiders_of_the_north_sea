"""
Game over screen - display results
"""
import pygame
from game.engine import GameEngine
from ui import config
from ui.components import Button


class GameOverScreen:
    """Game over screen showing results"""
    
    def __init__(self, screen: pygame.Surface, engine: GameEngine):
        self.screen = screen
        self.engine = engine
        
        # Menu button
        self.menu_button = Button(
            config.WINDOW_WIDTH // 2 - 150, 700, 300, 70,
            "Back to Menu",
            color=config.BLUE,
            text_color=config.WHITE,
            font_size=32
        )
    
    def handle_event(self, event: pygame.event.Event, on_menu: callable) -> bool:
        """
        Handle events
        Returns True if should return to menu
        """
        if self.menu_button.handle_event(event):
            on_menu()
            return True
        return False
    
    def update(self):
        """Update state"""
        mouse_pos = pygame.mouse.get_pos()
        self.menu_button.update(mouse_pos)
    
    def draw(self):
        """Draw game over screen"""
        self.screen.fill(config.WHITE)
        
        # Title
        title = config.FONT_LARGE.render("Game Over!", True, config.BLACK)
        title_rect = title.get_rect(center=(config.WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Winner
        winner = self.engine.get_winner()
        if winner:
            winner_text = config.FONT_MEDIUM.render(f"Winner: {winner.name}!", True, config.GREEN)
            winner_rect = winner_text.get_rect(center=(config.WINDOW_WIDTH // 2, 200))
            self.screen.blit(winner_text, winner_rect)
        
        # Final scores
        scores_title = config.FONT_MEDIUM.render("Final Scores:", True, config.BLACK)
        scores_rect = scores_title.get_rect(center=(config.WINDOW_WIDTH // 2, 300))
        self.screen.blit(scores_title, scores_rect)
        
        # Sort players by VP
        sorted_players = sorted(
            self.engine.state.players,
            key=lambda p: p.get_final_vp(),
            reverse=True
        )
        
        scores_y = 350
        for i, player in enumerate(sorted_players):
            # Rank, name, VP
            score_text = f"{i+1}. {player.name}: {player.get_final_vp()} VP"
            score_surface = config.FONT_SMALL.render(score_text, True, config.BLACK)
            score_rect = score_surface.get_rect(center=(config.WINDOW_WIDTH // 2, scores_y + i * 40))
            self.screen.blit(score_surface, score_rect)
        
        # Game summary
        summary = self.engine.get_game_summary()
        summary_y = scores_y + len(sorted_players) * 40 + 50
        summary_text = f"Rounds: {summary['round']} | Actions: {summary['actions_taken']}"
        summary_surface = config.FONT_SMALL.render(summary_text, True, config.DARK_GRAY)
        summary_rect = summary_surface.get_rect(center=(config.WINDOW_WIDTH // 2, summary_y))
        self.screen.blit(summary_surface, summary_rect)
        
        # Menu button
        self.menu_button.draw(self.screen)
