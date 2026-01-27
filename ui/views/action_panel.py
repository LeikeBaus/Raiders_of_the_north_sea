"""
Action panel - displays legal actions for current player
"""
import pygame
from typing import List, Callable
from game.actions import Action
from ui import config


class ActionPanel:
    """Render legal actions list"""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font_title = pygame.font.Font(None, 24)
        self.font_action = pygame.font.Font(None, config.ACTION_FONT_SIZE)
        self.font_tiny = pygame.font.Font(None, 14)
        self.scroll_offset = 0
        self.hovered_idx = None
    
    def draw(self, screen: pygame.Surface, actions: List[Action], on_action_click: Callable[[Action], None]):
        """Draw action panel with clickable actions"""
        # Background
        pygame.draw.rect(screen, config.WHITE, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, config.BLACK, (self.x, self.y, self.width, self.height), 3)
        
        # Title
        title = self.font_title.render(f"Legal Actions ({len(actions)})", True, config.BLACK)
        screen.blit(title, (self.x + 10, self.y + 10))
        
        # Instructions
        inst = self.font_tiny.render("Click action to execute | Scroll: mouse wheel", True, config.GRAY)
        screen.blit(inst, (self.x + 10, self.y + 40))
        
        if not actions:
            no_actions = self.font_action.render("No legal actions!", True, config.RED)
            screen.blit(no_actions, (self.x + 10, self.y + 70))
            return
        
        # Draw action list
        visible_actions = actions[self.scroll_offset:self.scroll_offset + config.ACTIONS_PER_PAGE]
        
        action_y = self.y + 70
        mouse_pos = pygame.mouse.get_pos()
        
        for i, action in enumerate(visible_actions):
            actual_idx = i + self.scroll_offset
            action_rect = pygame.Rect(
                self.x + 10,
                action_y + i * config.ACTION_ITEM_HEIGHT,
                self.width - 20,
                config.ACTION_ITEM_HEIGHT - 2
            )
            
            # Check hover
            is_hovered = action_rect.collidepoint(mouse_pos)
            color = config.GREEN if is_hovered else config.LIGHT_GRAY
            
            # Draw action button
            pygame.draw.rect(screen, color, action_rect)
            pygame.draw.rect(screen, config.BLACK, action_rect, 1)
            
            # Action text
            action_text = self._get_action_text(action)
            text_surface = self.font_action.render(action_text, True, config.BLACK)
            screen.blit(text_surface, (action_rect.x + 5, action_rect.y + 5))
            
            # Store hover state for click handling
            if is_hovered:
                self.hovered_idx = actual_idx
        
        # Scroll indicator
        if len(actions) > config.ACTIONS_PER_PAGE:
            scroll_text = f"Showing {self.scroll_offset + 1}-{min(self.scroll_offset + config.ACTIONS_PER_PAGE, len(actions))} of {len(actions)}"
            scroll_surface = self.font_tiny.render(scroll_text, True, config.GRAY)
            screen.blit(scroll_surface, (self.x + 10, self.y + self.height - 25))
    
    def handle_click(self, actions: List[Action], on_action_click: Callable[[Action], None]) -> bool:
        """
        Handle click on action panel
        Returns True if action was clicked
        """
        if self.hovered_idx is not None and self.hovered_idx < len(actions):
            on_action_click(actions[self.hovered_idx])
            self.hovered_idx = None
            return True
        return False
    
    def handle_scroll(self, direction: int, actions: List[Action]):
        """Handle scroll wheel"""
        if direction > 0:  # Scroll up
            self.scroll_offset = max(0, self.scroll_offset - 1)
        elif direction < 0:  # Scroll down
            max_scroll = max(0, len(actions) - config.ACTIONS_PER_PAGE)
            self.scroll_offset = min(max_scroll, self.scroll_offset + 1)
    
    def reset_scroll(self):
        """Reset scroll to top"""
        self.scroll_offset = 0
        self.hovered_idx = None
    
    def _get_action_text(self, action: Action) -> str:
        """Get readable text for action"""
        from game.actions import PlaceWorkerAction, PickupWorkerAction, HireCrewAction, PlayCardTownHallAction, RaidAction
        
        if isinstance(action, PlaceWorkerAction):
            return f"Place worker at {self._get_building_name(action.building_id)}"
        elif isinstance(action, PickupWorkerAction):
            return f"Pickup worker from {self._get_building_name(action.building_id)}"
        elif isinstance(action, HireCrewAction):
            return f"Hire crew: {action.card_id}"
        elif isinstance(action, PlayCardTownHallAction):
            return f"Play at Town Hall: {action.card_id}"
        elif isinstance(action, RaidAction):
            return f"Raid {action.location_id} ({len(action.crew_ids)} crew)"
        else:
            return action.get_description()
    
    def _get_building_name(self, building_id: str) -> str:
        """Get building name from ID"""
        from game.board import get_board_database
        building = get_board_database().get_building(building_id)
        return building.name if building else building_id
