"""
Board view - displays village buildings, raid locations, and offerings
"""
import pygame
from typing import Optional
from game.state import GameState
from game.board import get_board_database
from ui.config import *


class BoardView:
    """Render the game board"""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font_building = pygame.font.Font(None, 16)
        self.font_tiny = pygame.font.Font(None, 12)
        self.board_db = get_board_database()
    
    def draw(self, screen: pygame.Surface, state: GameState):
        """Draw the complete board"""
        # Background
        pygame.draw.rect(screen, LIGHT_GRAY, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 3)
        
        # Title
        title_font = pygame.font.Font(None, 24)
        title = title_font.render("Game Board", True, BLACK)
        screen.blit(title, (self.x + 10, self.y + 10))
        
        # Draw village buildings
        self._draw_village_buildings(screen, state)
        
        # Draw raid locations
        self._draw_raid_locations(screen, state)
        
        # Draw offerings area
        self._draw_offerings(screen, state)
    
    def _draw_village_buildings(self, screen: pygame.Surface, state: GameState):
        """Draw village buildings with workers"""
        # Village area label
        label = self.font_building.render("Village Buildings:", True, BLACK)
        screen.blit(label, (self.x + VILLAGE_AREA_X, self.y + 50))
        
        # Get building positions
        buildings = self.board_db.buildings
        
        # Arrange in grid
        buildings_per_row = 2
        for i, building in enumerate(buildings):
            row = i // buildings_per_row
            col = i % buildings_per_row
            
            bldg_x = self.x + VILLAGE_AREA_X + col * (VILLAGE_BUILDING_WIDTH + VILLAGE_BUILDING_SPACING)
            bldg_y = self.y + 80 + row * (VILLAGE_BUILDING_HEIGHT + VILLAGE_BUILDING_SPACING)
            
            self._draw_building(screen, building, bldg_x, bldg_y, state)
    
    def _draw_building(self, screen: pygame.Surface, building, x: int, y: int, state: GameState):
        """Draw a single building"""
        # Background
        pygame.draw.rect(screen, DARK_GREEN, (x, y, VILLAGE_BUILDING_WIDTH, VILLAGE_BUILDING_HEIGHT))
        pygame.draw.rect(screen, BLACK, (x, y, VILLAGE_BUILDING_WIDTH, VILLAGE_BUILDING_HEIGHT), 2)
        
        # Building name
        name = building.name[:12]  # Truncate
        name_surface = self.font_tiny.render(name, True, WHITE)
        screen.blit(name_surface, (x + 5, y + 5))
        
        # Worker slots
        workers = state.get_worker_at_building(building.id)
        slots_text = f"{len(workers)}/{building.worker_slots}"
        slots_surface = self.font_tiny.render(slots_text, True, YELLOW)
        screen.blit(slots_surface, (x + 5, y + 20))
        
        # Draw worker icons
        for i, worker in enumerate(workers[:building.worker_slots]):
            worker_x = x + 5 + i * 15
            worker_y = y + 40
            
            # Color based on worker color
            if worker.worker_color.value == 'black':
                color = BLACK
            elif worker.worker_color.value == 'grey':
                color = GRAY
            else:  # white
                color = WHITE
            
            pygame.draw.circle(screen, color, (worker_x, worker_y), 6)
            pygame.draw.circle(screen, BLACK, (worker_x, worker_y), 6, 1)
        
        # Action hint
        action_type = building.action.get("type", "")
        hint = ""
        if action_type == "draw_cards":
            hint = "Draw"
        elif action_type == "gain_by_worker_color":
            hint = "Gain"
        elif action_type == "play_card_town_hall":
            hint = "TownHall"
        
        if hint:
            hint_surface = self.font_tiny.render(hint, True, YELLOW)
            screen.blit(hint_surface, (x + 5, y + 60))
    
    def _draw_raid_locations(self, screen: pygame.Surface, state: GameState):
        """Draw raid locations"""
        # Raid area label
        label = self.font_building.render("Raid Locations:", True, BLACK)
        screen.blit(label, (self.x + RAID_AREA_X, self.y + 50))
        
        raids = self.board_db.raids
        
        # Arrange raids vertically by type
        current_y = self.y + 80
        
        for raid in raids:
            self._draw_raid(screen, raid, self.x + RAID_AREA_X, current_y, state)
            current_y += 40  # Compact layout
    
    def _draw_raid(self, screen: pygame.Surface, raid, x: int, y: int, state: GameState):
        """Draw a single raid location"""
        # Small box for raid
        box_width = 180
        box_height = 35
        
        # Color by type
        if "Harbour" in raid.name:
            color = BLUE
        elif "Outpost" in raid.name:
            color = ORANGE
        elif "Monastery" in raid.name:
            color = PURPLE
        else:  # Fortress
            color = RED
        
        pygame.draw.rect(screen, color, (x, y, box_width, box_height))
        pygame.draw.rect(screen, BLACK, (x, y, box_width, box_height), 2)
        
        # Raid name
        name = raid.name[:15]
        name_surface = self.font_tiny.render(name, True, WHITE)
        screen.blit(name_surface, (x + 5, y + 5))
        
        # Show plunder remaining (sum across sublocations)
        total_plunder = sum(
            rs.plunder_remaining for rs in state.raid_states
            if rs.location_id == raid.id
        )
        plunder_text = f"Plunder: {total_plunder}"
        plunder_surface = self.font_tiny.render(plunder_text, True, YELLOW)
        screen.blit(plunder_surface, (x + 5, y + 20))
    
    def _draw_offerings(self, screen: pygame.Surface, state: GameState):
        """Draw offering tiles area"""
        # Offerings label
        label = self.font_building.render("Offerings:", True, BLACK)
        screen.blit(label, (self.x + OFFERING_AREA_X, self.y + 50))
        
        # Draw visible offerings
        for i, offering in enumerate(state.visible_offerings[:4]):
            off_x = self.x + OFFERING_AREA_X + i * (OFFERING_TILE_SIZE + 10)
            off_y = self.y + 80
            
            # Offering tile
            pygame.draw.rect(screen, GOLD, (off_x, off_y, OFFERING_TILE_SIZE, OFFERING_TILE_SIZE))
            pygame.draw.rect(screen, BLACK, (off_x, off_y, OFFERING_TILE_SIZE, OFFERING_TILE_SIZE), 2)
            
            # VP
            vp_text = f"{offering.vp}VP"
            vp_surface = self.font_tiny.render(vp_text, True, BLACK)
            vp_rect = vp_surface.get_rect(center=(off_x + OFFERING_TILE_SIZE // 2, off_y + OFFERING_TILE_SIZE // 2))
            screen.blit(vp_surface, vp_rect)
        
        # Stack info
        stack_text = f"Stack: {len(state.offering_stack)}"
        stack_surface = self.font_tiny.render(stack_text, True, DARK_GRAY)
        screen.blit(stack_surface, (self.x + OFFERING_AREA_X, self.y + 150))
