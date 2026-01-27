"""
Board view - displays game board in 6-row grid layout
"""
import pygame
from typing import Optional, Tuple
from game.state import GameState
from game.board import get_board_database
from ui import config
from ui.components.icon_manager import draw_icon, load_icon, RESOURCE_ICONS, WORKER_ICONS


class BoardView:
    """Render the game board in 6-row grid layout"""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font_small = pygame.font.Font(None, config.scale(14))
        self.font_tiny = pygame.font.Font(None, config.scale(10))
        self.board_db = get_board_database()
        
        # Cache raid and building lookups
        self._raid_lookup = {raid.name: raid for raid in self.board_db.raids}
        self._building_lookup = {bldg.name: bldg for bldg in self.board_db.buildings}
    
    def draw(self, screen: pygame.Surface, state: GameState):
        """Draw the complete board"""
        # Background
        pygame.draw.rect(screen, config.LIGHT_GRAY, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, config.BLACK, (self.x, self.y, self.width, self.height), 3)
        
        # Row 1: Fortresses (XX_XX_XX)
        self._draw_fortresses(screen, state)
        
        # Row 2: Monastery 2, Monastery 1, Outpost 2 (XX_XX_XX)
        self._draw_row2(screen, state)
        
        # Row 3: Harbour 3, Outpost 1 (XXX_XX)
        self._draw_row3(screen, state)
        
        # Row 4: Harbour 2, Harbour 1 (XXX_XXX)
        self._draw_row4(screen, state)
        
        # Row 5: Buildings (Gate House, Treasury, Town Hall, Barracks) + Offering 3
        self._draw_row5(screen, state)
        
        # Row 6: Buildings (Armoury, Mill, Silversmith, Long House) + Offerings 1 & 2
        self._draw_row6(screen, state)
    
    def _draw_fortresses(self, screen: pygame.Surface, state: GameState):
        """Draw Row 1: 3 fortresses with 2 slots each"""
        y = config.FORTRESS_Y
        slot_width = config.FORTRESS_SLOT_WIDTH
        
        # Find all fortress raids
        fortresses = [r for r in self.board_db.raids if r.type == 'fortress']
        
        x_pos = self.x + config.BOX_SPACING
        for i, fortress in enumerate(fortresses):
            # Draw 2 slots per fortress
            for j, subloc in enumerate(fortress.sublocations[:2]):  # Only first 2 slots
                self._draw_raid_slot(screen, fortress, subloc, x_pos, y, slot_width, state)
                x_pos += slot_width + config.BOX_SPACING
            
            # Add extra space between fortress groups
            if i < len(fortresses) - 1:
                x_pos += config.BOX_SPACING
    
    def _draw_row2(self, screen: pygame.Surface, state: GameState):
        """Draw Row 2: Monastery 2, Monastery 1, Outpost 2"""
        y = config.ROW2_Y
        slot_width = config.FORTRESS_SLOT_WIDTH
        
        # Get raids
        mon2 = self._raid_lookup.get("Monastery 2")
        mon1 = self._raid_lookup.get("Monastery 1")
        out2 = self._raid_lookup.get("Outpost 2")
        
        x_pos = self.x + config.BOX_SPACING
        
        # Monastery 2 (2 slots)
        if mon2:
            for subloc in mon2.sublocations:
                self._draw_raid_slot(screen, mon2, subloc, x_pos, y, slot_width, state)
                x_pos += slot_width + config.BOX_SPACING
        
        x_pos += config.BOX_SPACING  # Extra space
        
        # Monastery 1 (2 slots)
        if mon1:
            for subloc in mon1.sublocations:
                self._draw_raid_slot(screen, mon1, subloc, x_pos, y, slot_width, state)
                x_pos += slot_width + config.BOX_SPACING
        
        x_pos += config.BOX_SPACING  # Extra space
        
        # Outpost 2 (2 slots)
        if out2:
            for subloc in out2.sublocations:
                self._draw_raid_slot(screen, out2, subloc, x_pos, y, slot_width, state)
                x_pos += slot_width + config.BOX_SPACING
    
    def _draw_row3(self, screen: pygame.Surface, state: GameState):
        """Draw Row 3: Harbour 3 (3 slots), Outpost 1 (2 slots)"""
        y = config.ROW3_Y
        
        har3 = self._raid_lookup.get("Harbour 3")
        out1 = self._raid_lookup.get("Outpost 1")
        
        x_pos = self.x + config.BOX_SPACING
        slot_width = config.FORTRESS_SLOT_WIDTH
        
        # Harbour 3 (3 slots)
        if har3:
            for subloc in har3.sublocations:
                self._draw_raid_slot(screen, har3, subloc, x_pos, y, slot_width, state)
                x_pos += slot_width + config.BOX_SPACING
        
        x_pos += config.BOX_SPACING  # Extra space
        
        # Outpost 1 (2 slots)
        if out1:
            for subloc in out1.sublocations:
                self._draw_raid_slot(screen, out1, subloc, x_pos, y, slot_width, state)
                x_pos += slot_width + config.BOX_SPACING
    
    def _draw_row4(self, screen: pygame.Surface, state: GameState):
        """Draw Row 4: Harbour 2 (3 slots), Harbour 1 (3 slots)"""
        y = config.ROW4_Y
        
        har2 = self._raid_lookup.get("Harbour 2")
        har1 = self._raid_lookup.get("Harbour 1")
        
        x_pos = self.x + config.BOX_SPACING
        slot_width = config.FORTRESS_SLOT_WIDTH
        
        # Harbour 2
        if har2:
            for subloc in har2.sublocations:
                self._draw_raid_slot(screen, har2, subloc, x_pos, y, slot_width, state)
                x_pos += slot_width + config.BOX_SPACING
        
        x_pos += config.BOX_SPACING  # Extra space
        
        # Harbour 1
        if har1:
            for subloc in har1.sublocations:
                self._draw_raid_slot(screen, har1, subloc, x_pos, y, slot_width, state)
                x_pos += slot_width + config.BOX_SPACING
    
    def _draw_row5(self, screen: pygame.Surface, state: GameState):
        """Draw Row 5: Gate House, Treasury, Town Hall, Barracks + Offering 3"""
        y = config.ROW5_Y
        
        buildings = ["Gate House", "Treasury", "Town Hall", "Barracks"]
        x_pos = self.x + config.BOX_SPACING
        
        for bldg_name in buildings:
            bldg = self._building_lookup.get(bldg_name)
            if bldg:
                self._draw_building(screen, bldg, x_pos, y, config.BUILDING_SLOT_WIDTH, state)
            x_pos += config.BUILDING_SLOT_WIDTH + config.BOX_SPACING
        
        # Offering 3 (right side)
        if len(state.visible_offerings) >= 3:
            self._draw_offering(screen, state.visible_offerings[2], 
                              config.OFFERING_AREA_X, y, state)
    
    def _draw_row6(self, screen: pygame.Surface, state: GameState):
        """Draw Row 6: Armoury, Mill, Silversmith, Long House + Offerings 1 & 2"""
        y = config.ROW6_Y
        
        buildings = ["Armoury", "Mill", "Silversmith", "Long House"]
        x_pos = self.x + config.BOX_SPACING
        
        for bldg_name in buildings:
            bldg = self._building_lookup.get(bldg_name)
            if bldg:
                self._draw_building(screen, bldg, x_pos, y, config.BUILDING_SLOT_WIDTH, state)
            x_pos += config.BUILDING_SLOT_WIDTH + config.BOX_SPACING
        
        # Offerings 1 and 2 (right side)
        off_y = y
        if len(state.visible_offerings) >= 1:
            self._draw_offering(screen, state.visible_offerings[0], 
                              config.OFFERING_AREA_X, off_y, state)
        
        if len(state.visible_offerings) >= 2:
            self._draw_offering(screen, state.visible_offerings[1], 
                              config.OFFERING_AREA_X + config.OFFERING_TILE_SIZE + config.BOX_SPACING, 
                              off_y, state)
    
    def _draw_raid_slot(self, screen: pygame.Surface, raid, subloc, x: int, y: int, 
                       width: int, state: GameState):
        """Draw a single raid slot"""
        # Find state for this sublocation
        subloc_state = next(
            (rs for rs in state.raid_states 
             if rs.location_id == raid.id and rs.sublocation_id == subloc.id),
            None
        )
        
        # Color by raid type
        color_map = {
            'harbour': config.BLUE,
            'outpost': config.ORANGE,
            'monastery': config.PURPLE,
            'fortress': config.RED
        }
        color = color_map.get(raid.type, config.GRAY)
        
        # Draw slot box
        pygame.draw.rect(screen, color, (x, y, width, config.SLOT_HEIGHT))
        pygame.draw.rect(screen, config.BLACK, (x, y, width, config.SLOT_HEIGHT), 2)
        
        # Draw raid name (abbreviated)
        name_text = raid.name[:8]
        name_surface = self.font_tiny.render(name_text, True, config.WHITE)
        screen.blit(name_surface, (x + 3, y + 3))
        
        # Draw worker icon if present
        worker_icon_name = WORKER_ICONS.get(subloc.worker_on_spot, 'worker_black')
        worker_icon = load_icon(worker_icon_name, config.WORKER_ICON_SIZE)
        if worker_icon:
            screen.blit(worker_icon, (x + 3, y + 18))
        
        # Draw plunder icon (what type of plunder is here)
        plunder_remaining = subloc_state.plunder_remaining if subloc_state else subloc.plunder
        if plunder_remaining > 0:
            # Show plunder count
            plunder_text = str(plunder_remaining)
            plunder_surface = self.font_small.render(plunder_text, True, config.GOLD)
            screen.blit(plunder_surface, (x + width - 20, y + 25))
    
    def _draw_building(self, screen: pygame.Surface, building, x: int, y: int, 
                      width: int, state: GameState):
        """Draw a single building"""
        # Background
        pygame.draw.rect(screen, config.DARK_GREEN, (x, y, width, config.BUILDING_SLOT_HEIGHT))
        pygame.draw.rect(screen, config.BLACK, (x, y, width, config.BUILDING_SLOT_HEIGHT), 2)
        
        # Building name (abbreviated)
        name = building.name[:10]
        name_surface = self.font_small.render(name, True, config.WHITE)
        screen.blit(name_surface, (x + 3, y + 3))
        
        # Draw worker icons (not count)
        workers = state.get_worker_at_building(building.id)
        worker_x = x + 3
        worker_y = y + 25
        
        for worker in workers[:building.worker_slots]:
            worker_icon_name = WORKER_ICONS.get(worker.worker_color.value, 'worker_black')
            icon = load_icon(worker_icon_name, config.WORKER_ICON_SIZE)
            if icon:
                screen.blit(icon, (worker_x, worker_y))
                worker_x += config.WORKER_ICON_SIZE + 3
    
    def _draw_offering(self, screen: pygame.Surface, offering, x: int, y: int, state: GameState):
        """Draw a single offering tile"""
        size = config.OFFERING_TILE_SIZE
        
        # Offering tile
        pygame.draw.rect(screen, config.GOLD, (x, y, size, size))
        pygame.draw.rect(screen, config.BLACK, (x, y, size, size), 2)
        
        # VP with icon
        vp_icon_size = config.scale(16)
        vp_icon = load_icon(RESOURCE_ICONS['vp'], vp_icon_size)
        if vp_icon:
            icon_x = x + size // 2 - vp_icon_size // 2
            screen.blit(vp_icon, (icon_x, y + 5))
            
        vp_text = f"{offering.vp}"
        vp_surface = self.font_small.render(vp_text, True, config.BLACK)
        vp_rect = vp_surface.get_rect(center=(x + size // 2, y + 25))
        screen.blit(vp_surface, vp_rect)
        
        # Draw requirement icons
        req_y = y + 35
        icon_size = config.scale(12)
        spacing = 2
        
        total_icons = sum(offering.requirements.values())
        start_x = x + (size - total_icons * (icon_size + spacing)) // 2
        
        icon_x = start_x
        for resource, amount in offering.requirements.items():
            icon_name = RESOURCE_ICONS.get(resource, resource)
            for _ in range(amount):
                icon = load_icon(icon_name, icon_size)
                if icon:
                    screen.blit(icon, (icon_x, req_y))
                else:
                    # Fallback
                    resource_colors = {
                        'livestock': config.BROWN,
                        'gold': config.GOLD,
                        'iron': config.DARK_GRAY,
                        'silver': config.LIGHT_GRAY
                    }
                    color = resource_colors.get(resource, config.BLACK)
                    pygame.draw.rect(screen, color, (icon_x, req_y, icon_size, icon_size))
                    pygame.draw.rect(screen, config.BLACK, (icon_x, req_y, icon_size, icon_size), 1)
                icon_x += icon_size + spacing
    
    def get_hover_info(self, mouse_pos, state: GameState):
        """Get information about what the mouse is hovering over"""
        # TODO: Implement hover detection for new layout
        # For now, return None
        return None
