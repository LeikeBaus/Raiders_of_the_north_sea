"""
Reusable button component
"""
import pygame
from typing import Callable, Optional, Tuple
from ui.config import *


class Button:
    """Interactive button component"""
    
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        on_click: Optional[Callable] = None,
        color: Tuple[int, int, int] = GREEN,
        hover_color: Tuple[int, int, int] = None,
        text_color: Tuple[int, int, int] = BLACK,
        font_size: int = BUTTON_FONT_SIZE
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.on_click = on_click
        self.color = color
        self.hover_color = hover_color or self._lighten_color(color)
        self.text_color = text_color
        self.font = pygame.font.Font(None, font_size)
        self.is_hovered = False
    
    def _lighten_color(self, color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Make color lighter for hover effect"""
        return tuple(min(255, c + 30) for c in color)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame event
        Returns True if button was clicked
        """
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                if self.on_click:
                    self.on_click()
                return True
        
        return False
    
    def update(self, mouse_pos: Tuple[int, int]):
        """Update hover state"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def draw(self, screen: pygame.Surface):
        """Draw button"""
        # Background
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, current_color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        # Text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
