"""
History view - displays recent game actions/moves
"""
import pygame
from typing import List
from ui import config


# Player colors
PLAYER_COLORS = {
    0: config.RED,      # Player 1
    1: config.YELLOW,   # Player 2
    2: config.GREEN,    # Player 3
    3: config.BLUE,     # Player 4
}


class HistoryView:
    """Display recent game history"""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = pygame.font.Font(None, config.scale(12))
        self.history: List[tuple] = []  # List of (player_idx, message)
        self.max_entries = 20
    
    def add_entry(self, player_idx: int, message: str):
        """Add a history entry"""
        self.history.append((player_idx, message))
        # Keep only recent entries
        if len(self.history) > self.max_entries:
            self.history = self.history[-self.max_entries:]
    
    def clear(self):
        """Clear history"""
        self.history = []
    
    def draw(self, screen: pygame.Surface):
        """Draw the history panel"""
        # Background
        pygame.draw.rect(screen, config.WHITE, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, config.BLACK, (self.x, self.y, self.width, self.height), 2)
        
        # Title
        title = self.font.render("History", True, config.BLACK)
        screen.blit(title, (self.x + 5, self.y + 5))
        
        # Draw entries (most recent at bottom)
        y_offset = self.y + 25
        line_height = config.scale(14)
        
        # Calculate how many entries fit
        available_height = self.height - 30
        max_visible = int(available_height / line_height)
        
        # Show most recent entries that fit
        visible_entries = self.history[-max_visible:] if len(self.history) > max_visible else self.history
        
        for player_idx, message in visible_entries:
            # Get player color
            color = PLAYER_COLORS.get(player_idx, config.BLACK)
            
            # Truncate message if too long
            max_chars = int(self.width / 6)  # Rough estimate
            display_msg = message[:max_chars] if len(message) > max_chars else message
            
            # Render in player color
            text_surface = self.font.render(display_msg, True, color)
            
            # Check if we're out of space
            if y_offset + line_height > self.y + self.height - 5:
                break
                
            screen.blit(text_surface, (self.x + 5, y_offset))
            y_offset += line_height
