"""
Resource display component
"""
import pygame
from typing import Dict
from ui.config import *


class ResourceBar:
    """Display player resources"""
    
    def __init__(self, x: int, y: int, width: int):
        self.x = x
        self.y = y
        self.width = width
        self.font = pygame.font.Font(None, RESOURCE_FONT_SIZE)
    
    def draw(self, screen: pygame.Surface, resources: Dict[str, int]):
        """
        Draw resource bar
        resources: dict with keys like 'silver', 'gold', 'provisions', etc.
        """
        resource_display = [
            ("Silver", resources.get('silver', 0), LIGHT_GRAY),
            ("Gold", resources.get('gold', 0), GOLD),
            ("Prov", resources.get('provisions', 0), BROWN),
            ("Iron", resources.get('iron', 0), DARK_GRAY),
            ("Stock", resources.get('livestock', 0), GREEN),
        ]
        
        item_width = 80
        current_x = self.x
        
        for name, amount, color in resource_display:
            # Background box
            box_rect = pygame.Rect(current_x, self.y, item_width, RESOURCE_ICON_SIZE)
            pygame.draw.rect(screen, color, box_rect)
            pygame.draw.rect(screen, BLACK, box_rect, 1)
            
            # Text
            text = f"{name}: {amount}"
            text_surface = self.font.render(text, True, BLACK)
            text_rect = text_surface.get_rect(center=box_rect.center)
            screen.blit(text_surface, text_rect)
            
            current_x += item_width + RESOURCE_SPACING


class CombatStats:
    """Display armour and valkyrie"""
    
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.font = pygame.font.Font(None, RESOURCE_FONT_SIZE)
    
    def draw(self, screen: pygame.Surface, armour: int, valkyrie: int):
        """Draw combat stats"""
        text = f"Armour: {armour} | Valkyrie: {valkyrie}"
        text_surface = self.font.render(text, True, BLACK)
        screen.blit(text_surface, (self.x, self.y))
