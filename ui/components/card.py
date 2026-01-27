"""
Card display component
"""
import pygame
from typing import Optional
from ui.config import *


class CardDisplay:
    """Display a single card"""
    
    def __init__(self, x: int, y: int, card_data: Optional[dict] = None, hidden: bool = False):
        self.x = x
        self.y = y
        self.card_data = card_data
        self.hidden = hidden
        self.font_name = pygame.font.Font(None, CARD_FONT_SIZE)
        self.font_tiny = pygame.font.Font(None, 10)
    
    def draw(self, screen: pygame.Surface):
        """Draw card"""
        card_rect = pygame.Rect(self.x, self.y, CARD_WIDTH, CARD_HEIGHT)
        
        if self.hidden or not self.card_data:
            # Card back
            pygame.draw.rect(screen, BROWN, card_rect)
            pygame.draw.rect(screen, BLACK, card_rect, 2)
            
            if not self.hidden:
                text = self.font_tiny.render("Card", True, WHITE)
                text_rect = text.get_rect(center=card_rect.center)
                screen.blit(text, text_rect)
        else:
            # Card face
            pygame.draw.rect(screen, WHITE, card_rect)
            pygame.draw.rect(screen, BLACK, card_rect, 2)
            
            # Card name (truncated)
            name = self.card_data.get('name', 'Card')[:12]
            name_surface = self.font_name.render(name, True, BLACK)
            screen.blit(name_surface, (self.x + 5, self.y + 5))
            
            # Cost
            cost = self.card_data.get('cost', 0)
            cost_text = self.font_tiny.render(f"${cost}", True, BLUE)
            screen.blit(cost_text, (self.x + 5, self.y + 25))
            
            # Strength
            strength = self.card_data.get('strength', 0)
            if strength > 0:
                str_text = self.font_tiny.render(f"STR:{strength}", True, RED)
                screen.blit(str_text, (self.x + 5, self.y + 40))
            
            # VP
            vp = self.card_data.get('vp', 0)
            if vp > 0:
                vp_text = self.font_tiny.render(f"VP:{vp}", True, GREEN)
                screen.blit(vp_text, (self.x + 5, self.y + 55))


def draw_card_list(screen: pygame.Surface, x: int, y: int, cards: list, hidden: bool = False, max_cards: int = 8):
    """Draw a horizontal list of cards"""
    for i, card in enumerate(cards[:max_cards]):
        card_x = x + i * (CARD_WIDTH + CARD_SPACING)
        card_display = CardDisplay(card_x, y, card.__dict__ if hasattr(card, '__dict__') else None, hidden)
        card_display.draw(screen)
    
    # Show count if more cards
    if len(cards) > max_cards:
        font = pygame.font.Font(None, 16)
        text = font.render(f"+{len(cards) - max_cards} more", True, GRAY)
        text_x = x + max_cards * (CARD_WIDTH + CARD_SPACING)
        screen.blit(text, (text_x, y + CARD_HEIGHT // 2))
