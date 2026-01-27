"""
Menu screen - player setup
"""
import pygame
from typing import Callable
from ui import config
from ui.components import Button


class MenuScreen:
    """Main menu for game setup"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.num_players = 2
        self.player_types = [True, True]  # True = Human, False = AI
        
        # Buttons
        self._create_buttons()
    
    def _create_buttons(self):
        """Create menu buttons"""
        center_x = config.WINDOW_WIDTH // 2
        
        # Player count buttons (2-4)
        self.player_buttons = []
        for i in range(2, 5):
            x = center_x - 150 + (i - 2) * 120
            button = Button(
                x, 250, 100, 50,
                str(i),
                on_click=lambda n=i: self._set_player_count(n),
                color=config.LIGHT_GRAY
            )
            self.player_buttons.append(button)
        
        # Start button
        self.start_button = Button(
            center_x - 100, 500, 200, 70,
            "Start Game",
            color=config.GREEN,
            font_size=32
        )
    
    def _set_player_count(self, count: int):
        """Set number of players"""
        self.num_players = count
        self.player_types = [True] * count
        self._update_button_colors()
    
    def _update_button_colors(self):
        """Update button colors based on selection"""
        for i, button in enumerate(self.player_buttons):
            selected = (i + 2) == self.num_players
            button.color = config.GREEN if selected else config.LIGHT_GRAY
            button.hover_color = button._lighten_color(button.color)
    
    def handle_event(self, event: pygame.event.Event, on_start: Callable):
        """Handle events"""
        # Player count buttons
        for button in self.player_buttons:
            button.handle_event(event)
        
        # Start button
        if self.start_button.handle_event(event):
            on_start(self.num_players, self.player_types)
    
    def update(self):
        """Update menu state"""
        mouse_pos = pygame.mouse.get_pos()
        for button in self.player_buttons:
            button.update(mouse_pos)
        self.start_button.update(mouse_pos)
        
        self._update_button_colors()
    
    def draw(self):
        """Draw menu"""
        self.screen.fill(config.WHITE)
        
        # Title
        title = config.FONT_LARGE.render("Raiders of the North Sea", True, config.BLACK)
        title_rect = title.get_rect(center=(config.WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = config.FONT_MEDIUM.render("Select Number of Players:", True, config.BLACK)
        subtitle_rect = subtitle.get_rect(center=(config.WINDOW_WIDTH // 2, 200))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Player buttons
        for button in self.player_buttons:
            button.draw(self.screen)
        
        # Player info
        info_y = 350
        for i in range(self.num_players):
            text = f"Player {i+1}: Human"
            player_text = config.FONT_SMALL.render(text, True, config.BLACK)
            player_rect = player_text.get_rect(center=(config.WINDOW_WIDTH // 2, info_y + i * 30))
            self.screen.blit(player_text, player_rect)
        
        # Start button
        self.start_button.draw(self.screen)
        
        # Instructions
        instructions = [
            "All players are human (AI coming soon)",
            "Press ESC during game to return to menu"
        ]
        for i, instruction in enumerate(instructions):
            text = config.FONT_TINY.render(instruction, True, config.GRAY)
            text_rect = text.get_rect(center=(config.WINDOW_WIDTH // 2, 650 + i * 25))
            self.screen.blit(text, text_rect)
