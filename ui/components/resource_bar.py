"""
Resource display component
"""
import pygame
from typing import Dict
from ui import config
from ui.components.icon_manager import draw_icon_with_text, RESOURCE_ICONS


class ResourceBar:
    """Display player resources"""
    
    def __init__(self, x: int, y: int, width: int):
        self.x = x
        self.y = y
        self.width = width
        self.font = pygame.font.Font(None, config.RESOURCE_FONT_SIZE)
    
    def draw(self, screen: pygame.Surface, resources: Dict[str, int]):
        """
        Draw resource bar with icons
        resources: dict with keys like 'silver', 'gold', 'provisions', etc.
        """
        resource_display = [
            ('silver', resources.get('silver', 0)),
            ('gold', resources.get('gold', 0)),
            ('provisions', resources.get('provisions', 0)),
            ('iron', resources.get('iron', 0)),
            ('livestock', resources.get('livestock', 0)),
        ]
        
        current_x = self.x
        icon_size = config.RESOURCE_ICON_SIZE
        
        for resource_name, amount in resource_display:
            icon_name = RESOURCE_ICONS.get(resource_name, resource_name)
            width_used = draw_icon_with_text(
                screen, icon_name, current_x, self.y,
                icon_size, str(amount), self.font, config.BLACK
            )
            current_x += width_used


class CombatStats:
    """Display armour and valkyrie"""
    
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.font = pygame.font.Font(None, config.RESOURCE_FONT_SIZE)
    
    def draw(self, screen: pygame.Surface, armour: int, valkyrie: int):
        """Draw combat stats with icons"""
        current_x = self.x
        icon_size = config.RESOURCE_ICON_SIZE
        
        # Armour (using strength icon as proxy)
        text_surface = self.font.render(f"Armour: {armour}", True, config.BLACK)
        screen.blit(text_surface, (current_x, self.y))
        current_x += text_surface.get_width() + 15
        
        # Valkyrie
        draw_icon_with_text(
            screen, RESOURCE_ICONS['valkyrie'], current_x, self.y,
            icon_size, str(valkyrie), self.font, config.BLACK
        )
