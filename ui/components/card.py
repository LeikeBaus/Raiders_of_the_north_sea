"""
Card display component
"""
import pygame
from typing import Optional
from pathlib import Path
from ui import config

# Cache for loaded card images
_card_image_cache = {}
_backside_image = None


def _get_card_image_path(card_name: str) -> Optional[Path]:
    """Get the image path for a card by name"""
    # Normalize card name to filename (lowercase, no spaces)
    filename = card_name.lower().replace(' ', '').replace("'", '') + '.jpg'
    image_path = Path(__file__).parent.parent.parent / 'res' / 'townsfolk' / filename
    
    if image_path.exists():
        return image_path
    return None


def _load_card_image(card_name: str, width: int, height: int) -> Optional[pygame.Surface]:
    """Load and cache a card image"""
    cache_key = (card_name, width, height)
    
    if cache_key in _card_image_cache:
        return _card_image_cache[cache_key]
    
    image_path = _get_card_image_path(card_name)
    if image_path:
        try:
            image = pygame.image.load(str(image_path))
            image = pygame.transform.scale(image, (width, height))
            _card_image_cache[cache_key] = image
            return image
        except Exception as e:
            print(f"Failed to load card image {image_path}: {e}")
    
    return None


def _load_backside_image(width: int, height: int) -> Optional[pygame.Surface]:
    """Load and cache the card backside image"""
    global _backside_image
    
    cache_key = ('backside', width, height)
    if cache_key in _card_image_cache:
        return _card_image_cache[cache_key]
    
    backside_path = Path(__file__).parent.parent.parent / 'res' / 'townsfolk' / 'backside.jpg'
    if backside_path.exists():
        try:
            image = pygame.image.load(str(backside_path))
            image = pygame.transform.scale(image, (width, height))
            _card_image_cache[cache_key] = image
            return image
        except Exception as e:
            print(f"Failed to load backside image: {e}")
    
    return None


class CardDisplay:
    """Display a single card"""
    
    def __init__(self, x: int, y: int, card_data: Optional[dict] = None, hidden: bool = False):
        self.x = x
        self.y = y
        self.card_data = card_data
        self.hidden = hidden
        self.font_name = pygame.font.Font(None, config.CARD_FONT_SIZE)
        self.font_tiny = pygame.font.Font(None, 10)
    
    def draw(self, screen: pygame.Surface):
        """Draw card"""
        card_rect = pygame.Rect(self.x, self.y, config.CARD_WIDTH, config.CARD_HEIGHT)
        
        if self.hidden or not self.card_data:
            # Card back - try to load backside image
            backside = _load_backside_image(config.CARD_WIDTH, config.CARD_HEIGHT)
            if backside:
                screen.blit(backside, (self.x, self.y))
            else:
                # Fallback to brown rectangle
                pygame.draw.rect(screen, config.BROWN, card_rect)
                pygame.draw.rect(screen, config.BLACK, card_rect, 2)
                
                if not self.hidden:
                    text = self.font_tiny.render("Card", True, config.WHITE)
                    text_rect = text.get_rect(center=card_rect.center)
                    screen.blit(text, text_rect)
        else:
            # Card face - try to load card image
            card_name = self.card_data.get('name', '') if isinstance(self.card_data, dict) else getattr(self.card_data, 'name', '')
            
            card_image = _load_card_image(card_name, config.CARD_WIDTH, config.CARD_HEIGHT)
            if card_image:
                screen.blit(card_image, (self.x, self.y))
            else:
                # Fallback to text rendering
                pygame.draw.rect(screen, config.WHITE, card_rect)
                pygame.draw.rect(screen, config.BLACK, card_rect, 2)
                
                # Card name (truncated)
                name = card_name[:12]
                name_surface = self.font_name.render(name, True, config.BLACK)
                screen.blit(name_surface, (self.x + 5, self.y + 5))
                
                # Cost
                cost = self.card_data.get('cost', 0) if isinstance(self.card_data, dict) else getattr(self.card_data, 'cost', 0)
                cost_text = self.font_tiny.render(f"${cost}", True, config.BLUE)
                screen.blit(cost_text, (self.x + 5, self.y + 25))
                
                # Strength
                strength = self.card_data.get('strength', 0) if isinstance(self.card_data, dict) else getattr(self.card_data, 'strength', 0)
                if strength > 0:
                    str_text = self.font_tiny.render(f"STR:{strength}", True, config.RED)
                    screen.blit(str_text, (self.x + 5, self.y + 40))
                
                # VP
                vp = self.card_data.get('vp', 0) if isinstance(self.card_data, dict) else getattr(self.card_data, 'vp', 0)
                if vp > 0:
                    vp_text = self.font_tiny.render(f"VP:{vp}", True, config.GREEN)
                    screen.blit(vp_text, (self.x + 5, self.y + 55))


def draw_card_list(screen: pygame.Surface, x: int, y: int, cards: list, hidden: bool = False, max_cards: int = 8):
    """Draw a horizontal list of cards"""
    for i, card in enumerate(cards[:max_cards]):
        card_x = x + i * (config.CARD_WIDTH + config.CARD_SPACING)
        card_display = CardDisplay(card_x, y, card.__dict__ if hasattr(card, '__dict__') else None, hidden)
        card_display.draw(screen)
    
    # Show count if more cards
    if len(cards) > max_cards:
        font = pygame.font.Font(None, 16)
        text = font.render(f"+{len(cards) - max_cards} more", True, config.GRAY)
        text_x = x + max_cards * (config.CARD_WIDTH + config.CARD_SPACING)
        screen.blit(text, (text_x, y + config.CARD_HEIGHT // 2))
