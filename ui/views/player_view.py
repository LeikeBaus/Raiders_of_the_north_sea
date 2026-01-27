"""
Player view - displays player information, resources, cards
"""
import pygame
from game.state import PlayerState
from ui import config
from ui.components import ResourceBar, CombatStats, draw_card_list


class PlayerView:
    """Render player information panel"""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font_title = pygame.font.Font(None, 24)
        self.font_info = pygame.font.Font(None, 18)
    
    def draw(self, screen: pygame.Surface, players: list, current_player_idx: int, viewing_player_idx: int):
        """
        Draw all players
        viewing_player_idx: which player is viewing (for card visibility)
        """
        # Background
        pygame.draw.rect(screen, config.WHITE, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, config.BLACK, (self.x, self.y, self.width, self.height), 3)
        
        # Title
        title = self.font_title.render("Players", True, config.BLACK)
        screen.blit(title, (self.x + 10, self.y + 10))
        
        # Draw each player
        num_players = len(players)
        panel_height = (self.height - 50) // num_players
        
        for i, player in enumerate(players):
            panel_y = self.y + 40 + i * panel_height
            self._draw_player(
                screen,
                player,
                self.x + 10,
                panel_y,
                self.width - 20,
                panel_height - 10,
                is_current=i == current_player_idx,
                show_cards=i == viewing_player_idx
            )
    
    def _draw_player(
        self,
        screen: pygame.Surface,
        player: PlayerState,
        x: int,
        y: int,
        width: int,
        height: int,
        is_current: bool,
        show_cards: bool
    ):
        """Draw single player panel"""
        # Background
        bg_color = config.YELLOW if is_current else config.LIGHT_GRAY
        pygame.draw.rect(screen, bg_color, (x, y, width, height))
        pygame.draw.rect(screen, config.BLACK, (x, y, width, height), 2)
        
        # Name and VP
        name_text = f"{player.name} - {player.vp} VP"
        name_surface = self.font_info.render(name_text, True, config.BLACK)
        screen.blit(name_surface, (x + 5, y + 5))
        
        # Worker in hand
        worker_text = f"Worker: {player.worker_in_hand.value if player.worker_in_hand else 'None'}"
        worker_surface = self.font_info.render(worker_text, True, config.DARK_BLUE)
        screen.blit(worker_surface, (x + 5, y + 25))
        
        # Resources
        resources = {
            'silver': player.silver,
            'gold': player.gold,
            'provisions': player.provisions,
            'iron': player.iron,
            'livestock': player.livestock
        }
        resource_bar = ResourceBar(x + 5, y + 50, width - 10)
        resource_bar.draw(screen, resources)
        
        # Combat stats
        combat = CombatStats(x + 5, y + 85)
        combat.draw(screen, player.armour, player.valkyrie)
        
        # Cards, crew, offerings count
        info_y = y + 105
        info_text = f"Hand: {len(player.hand)} | Crew: {len(player.crew)} | Offerings: {len(player.offerings)}"
        info_surface = self.font_info.render(info_text, True, config.DARK_GRAY)
        screen.blit(info_surface, (x + 5, info_y))
        
        # Show cards if this is the viewing player
        if show_cards and player.hand and height > 130:
            cards_y = y + height - 90
            draw_card_list(screen, x + 5, cards_y, player.hand, hidden=False, max_cards=6)
        elif not show_cards and player.hand:
            # Show card backs for other players
            cards_y = y + height - 90
            draw_card_list(screen, x + 5, cards_y, player.hand, hidden=True, max_cards=6)
    
    def get_hover_info(self, mouse_pos, players: list, viewing_player_idx: int):
        """
        Get information about what the mouse is hovering over
        Returns (object_type, object_data) or None
        """
        mx, my = mouse_pos
        
        num_players = len(players)
        panel_height = (self.height - 50) // num_players
        
        for i, player in enumerate(players):
            panel_y = self.y + 40 + i * panel_height
            panel_x = self.x + 10
            panel_width = self.width - 20
            panel_height_actual = panel_height - 10
            
            # Only show cards for viewing player
            if i == viewing_player_idx and player.hand:
                cards_y = panel_y + panel_height_actual - 90
                cards_x = panel_x + 5
                
                # Check each card
                for j, card in enumerate(player.hand[:6]):
                    card_x = cards_x + j * (config.CARD_WIDTH + config.CARD_SPACING)
                    
                    if (card_x <= mx <= card_x + config.CARD_WIDTH and
                        cards_y <= my <= cards_y + config.CARD_HEIGHT):
                        return ('card', card)
        
        return None
