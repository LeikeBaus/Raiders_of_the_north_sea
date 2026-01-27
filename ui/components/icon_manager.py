"""
Icon manager - loads and caches PNG icons
"""
import pygame
from typing import Optional, Dict, Tuple
from pathlib import Path

# Cache for loaded icons
_icon_cache: Dict[Tuple[str, int], pygame.Surface] = {}


def get_icon_path(icon_name: str) -> Optional[Path]:
    """Get the path to an icon file"""
    icon_path = Path(__file__).parent.parent.parent / 'res' / 'icons' / f'{icon_name}.png'
    if icon_path.exists():
        return icon_path
    return None


def load_icon(icon_name: str, size: int) -> Optional[pygame.Surface]:
    """
    Load and cache an icon
    
    Available icons:
    - dice, gold, iron, livestock, offering, provisions, silver
    - strength, valkyrie, VP
    - worker_black, worker_grey, worker_white
    """
    cache_key = (icon_name, size)
    
    if cache_key in _icon_cache:
        return _icon_cache[cache_key]
    
    icon_path = get_icon_path(icon_name)
    if icon_path:
        try:
            icon = pygame.image.load(str(icon_path))
            icon = pygame.transform.scale(icon, (size, size))
            _icon_cache[cache_key] = icon
            return icon
        except Exception as e:
            print(f"Failed to load icon {icon_name}: {e}")
    
    return None


def draw_icon(screen: pygame.Surface, icon_name: str, x: int, y: int, size: int):
    """Draw an icon at the specified position"""
    icon = load_icon(icon_name, size)
    if icon:
        screen.blit(icon, (x, y))
        return True
    return False


def draw_icon_with_text(screen: pygame.Surface, icon_name: str, x: int, y: int, 
                        size: int, text: str, font: pygame.font.Font, color: tuple):
    """Draw an icon with text next to it"""
    icon = load_icon(icon_name, size)
    if icon:
        screen.blit(icon, (x, y))
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (x + size + 5, y + (size - text_surface.get_height()) // 2))
        return size + 5 + text_surface.get_width() + 10
    else:
        # Fallback to text only
        text_surface = font.render(f"{icon_name}: {text}", True, color)
        screen.blit(text_surface, (x, y))
        return text_surface.get_width() + 10


# Resource icon names mapping
RESOURCE_ICONS = {
    'silver': 'silver',
    'gold': 'gold',
    'provisions': 'provisions',
    'iron': 'iron',
    'livestock': 'livestock',
    'valkyrie': 'valkyrie',
    'vp': 'VP',
    'strength': 'strength',
    'dice': 'dice',
    'offering': 'offering'
}

WORKER_ICONS = {
    'black': 'worker_black',
    'grey': 'worker_grey',
    'white': 'worker_white'
}
