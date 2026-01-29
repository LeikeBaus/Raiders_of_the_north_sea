"""
Board view - displays game board using coordinate-based positioning
"""
import pygame
import os
from typing import Optional, Tuple
from game.state import GameState
from game.board import get_board_database
from ui import config
from ui.components.icon_manager import draw_icon, load_icon, RESOURCE_ICONS, WORKER_ICONS


class BoardView:
    """Render the game board using coordinate-based positioning"""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font_small = pygame.font.Font(None, config.scale(14))
        self.font_tiny = pygame.font.Font(None, config.scale(10))
        self.font_vp = pygame.font.Font(None, config.OFFERING_STYLE['vp_font_size'])
        self.board_db = get_board_database()
        
        # Cache raid and building lookups
        self._raid_lookup = {raid.name: raid for raid in self.board_db.raids}
        self._building_lookup = {bldg.name: bldg for bldg in self.board_db.buildings}
        
        # Create sublocation ID to raid lookup
        self._subloc_to_raid = {}
        for raid in self.board_db.raids:
            for subloc in raid.sublocations:
                self._subloc_to_raid[subloc.id] = raid
        
        # Load background image
        self.background_image = None
        try:
            bg_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'res', 'background', 'board.png')
            self.background_image = pygame.image.load(bg_path)
            self.background_image = pygame.transform.scale(self.background_image, (width, height))
        except (pygame.error, FileNotFoundError) as e:
            print(f"Could not load background image: {e}. Using grey background.")
    
    def draw(self, screen: pygame.Surface, state: GameState):
        """Draw the complete board"""
        # Background
        if self.background_image:
            screen.blit(self.background_image, (self.x, self.y))
        else:
            pygame.draw.rect(screen, config.LIGHT_GRAY, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, config.BLACK, (self.x, self.y, self.width, self.height), 3)
        
        # Draw all raid locations using coordinate-based positioning
        self._draw_raid_locations(screen, state)
        
        # Draw all village buildings using coordinate-based positioning
        self._draw_village_buildings(screen, state)
        
        # Draw all offerings using coordinate-based positioning
        self._draw_offerings(screen, state)
    
    def _draw_raid_locations(self, screen: pygame.Surface, state: GameState):
        """Draw all raid sublocations using coordinate-based positioning"""
        for raid in self.board_db.raids:
            for subloc in raid.sublocations:
                if subloc.id in config.RAID_POSITIONS:
                    self._draw_raid_slot(screen, raid, subloc, state)
    
    def _draw_raid_slot(self, screen: pygame.Surface, raid, subloc, state: GameState):
        """Draw a single raid sublocation as a white rectangle with 60% transparency"""
        # Get middle point from config
        rel_x, rel_y = config.RAID_POSITIONS[subloc.id]
        center_x = self.x + rel_x
        center_y = self.y + rel_y
        
        # Calculate rectangle bounds
        rect_width = config.RAID_STYLE['width']
        rect_height = config.RAID_STYLE['height']
        rect_x = center_x - rect_width // 2
        rect_y = center_y - rect_height // 2
        
        # Create surface with alpha channel for transparency
        rect_surface = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)
        
        # Draw white rectangle with transparency
        color_with_alpha = (*config.RAID_STYLE['color'], config.RAID_STYLE['alpha'])
        pygame.draw.rect(rect_surface, color_with_alpha, (0, 0, rect_width, rect_height))
        
        # Draw border
        #pygame.draw.rect(rect_surface, config.RAID_STYLE['border_color'], 
        #                (0, 0, rect_width, rect_height), config.RAID_STYLE['border_width'])
        
        # Blit the transparent surface to screen
        screen.blit(rect_surface, (rect_x, rect_y))
        
        # Get sublocation state
        subloc_state = next(
            (rs for rs in state.raid_states 
             if rs.location_id == raid.id and rs.sublocation_id == subloc.id),
            None
        )
        
        # Draw plunder icons showing actual resources from game state
        if subloc_state:
            plunder_resources = subloc_state.plunder_resources
            # Flatten resource dict to list of individual resources
            resource_list = []
            for resource, count in sorted(plunder_resources.items()):
                resource_list.extend([resource] * count)
            
            if resource_list:
                icon_size = config.RAID_STYLE['plunder_icon_size']
                num_icons = min(len(resource_list), 4)  # Show max 4 icons
                
                # Calculate spacing for even distribution
                total_width = num_icons * icon_size
                spacing = (rect_width - total_width) // (num_icons + 1)
                
                icon_x = rect_x + spacing
                icon_y = center_y - icon_size // 2
                
                for i in range(num_icons):
                    resource = resource_list[i]
                    icon_name = RESOURCE_ICONS.get(resource, 'gold')
                    icon = load_icon(icon_name, icon_size)
                    if icon:
                        screen.blit(icon, (icon_x, icon_y))
                    icon_x += icon_size + spacing
                
                # If more than 4, show count
                if len(resource_list) > 4:
                    count_text = f"+{len(resource_list) - 4}"
                    count_surface = self.font_small.render(count_text, True, config.BLACK)
                    count_rect = count_surface.get_rect(center=(center_x, rect_y + rect_height - 10))
                    screen.blit(count_surface, count_rect)
        
        # Draw worker icon in top right corner if present
        if subloc.worker_on_spot:
            worker_icon_name = WORKER_ICONS.get(subloc.worker_on_spot, 'worker_black')
            worker_icon_size = config.RAID_STYLE['worker_icon_size']
            worker_icon = load_icon(worker_icon_name, worker_icon_size)
            if worker_icon:
                #worker_x = rect_x + rect_width - worker_icon_size - 5
                worker_x = rect_x + rect_width - worker_icon_size // 2
                worker_y = rect_y - rect_height + worker_icon_size * 4 // 3
                screen.blit(worker_icon, (worker_x, worker_y))
    
    def _draw_village_buildings(self, screen: pygame.Surface, state: GameState):
        """Draw all village buildings using coordinate-based positioning"""
        for building in self.board_db.buildings:
            if building.name in config.BUILDING_POSITIONS:
                self._draw_building(screen, building, state)
    
    def _draw_building(self, screen: pygame.Surface, building, state: GameState):
        """Draw a single building as a white ellipse with 60% transparency"""
        # Get middle point from config
        rel_x, rel_y = config.BUILDING_POSITIONS[building.name]
        center_x = self.x + rel_x
        center_y = self.y + rel_y
        
        # Calculate ellipse bounds
        radius_x = config.BUILDING_STYLE['radius_x']
        radius_y = config.BUILDING_STYLE['radius_y']
        rect_x = center_x - radius_x
        rect_y = center_y - radius_y
        width = radius_x * 2
        height = radius_y * 2
        
        # Create surface with alpha channel for transparency
        ellipse_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Draw white ellipse with transparency
        color_with_alpha = (*config.BUILDING_STYLE['color'], config.BUILDING_STYLE['alpha'])
        pygame.draw.ellipse(ellipse_surface, color_with_alpha, (0, 0, width, height))
        
        # Draw border
        pygame.draw.ellipse(ellipse_surface, config.BUILDING_STYLE['border_color'], 
                           (0, 0, width, height), config.BUILDING_STYLE['border_width'])
        
        # Blit the transparent surface to screen
        screen.blit(ellipse_surface, (rect_x, rect_y))
        
        # Draw worker icons in the middle if present
        workers = state.get_worker_at_building(building.id)
        if workers:
            worker_icon_size = config.BUILDING_STYLE['worker_icon_size']
            num_workers = len(workers[:building.worker_slots])
            
            # Calculate positions for multiple workers
            if num_workers == 1:
                worker_positions = [(center_x - worker_icon_size // 2, center_y - worker_icon_size // 2)]
            elif num_workers == 2:
                offset = worker_icon_size // 2 + 2
                worker_positions = [
                    (center_x - offset - worker_icon_size // 2, center_y - worker_icon_size // 2),
                    (center_x + offset - worker_icon_size // 2, center_y - worker_icon_size // 2)
                ]
            else:
                # For more workers, arrange in a circle
                worker_positions = []
                for i, worker in enumerate(workers[:building.worker_slots]):
                    angle = (2 * 3.14159 * i) / num_workers
                    wx = center_x + int(15 * pygame.math.Vector2(1, 0).rotate_rad(angle).x) - worker_icon_size // 2
                    wy = center_y + int(15 * pygame.math.Vector2(1, 0).rotate_rad(angle).y) - worker_icon_size // 2
                    worker_positions.append((wx, wy))
            
            # Draw each worker
            for i, worker in enumerate(workers[:building.worker_slots]):
                if i < len(worker_positions):
                    worker_icon_name = WORKER_ICONS.get(worker.worker_color.value, 'worker_black')
                    worker_icon = load_icon(worker_icon_name, worker_icon_size)
                    if worker_icon:
                        screen.blit(worker_icon, worker_positions[i])
    
    def _draw_offerings(self, screen: pygame.Surface, state: GameState):
        """Draw all visible offerings using offering slots"""
        # Place each visible offering on a slot
        for i, offering in enumerate(state.visible_offerings[:len(config.OFFERING_SLOTS)]):
            if i < len(config.OFFERING_SLOTS):
                self._draw_offering_at_slot(screen, offering, i, state)
    
    def _draw_offering_at_slot(self, screen: pygame.Surface, offering, slot_index: int, state: GameState):
        """Draw a single offering at the specified slot as a red rectangle with 60% transparency"""
        # Get middle point from slot configuration
        rel_x, rel_y = config.OFFERING_SLOTS[slot_index]
        center_x = self.x + rel_x
        center_y = self.y + rel_y
        
        # Calculate rectangle bounds
        rect_width = config.OFFERING_STYLE['width']
        rect_height = config.OFFERING_STYLE['height']
        rect_x = center_x - rect_width // 2
        rect_y = center_y - rect_height // 2
        
        # Create surface with alpha channel for transparency
        rect_surface = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)
        
        # Draw red rectangle with transparency
        color_with_alpha = (*config.OFFERING_STYLE['color'], config.OFFERING_STYLE['alpha'])
        pygame.draw.rect(rect_surface, color_with_alpha, (0, 0, rect_width, rect_height))
        
        # Draw border
        pygame.draw.rect(rect_surface, config.OFFERING_STYLE['border_color'], 
                        (0, 0, rect_width, rect_height), config.OFFERING_STYLE['border_width'])
        
        # Blit the transparent surface to screen
        screen.blit(rect_surface, (rect_x, rect_y))
        
        # Draw VP at top middle
        vp_text = f"{offering.vp} VP"
        vp_surface = self.font_vp.render(vp_text, True, config.BLACK)
        vp_rect = vp_surface.get_rect(center=(center_x, rect_y + 12))
        screen.blit(vp_surface, vp_rect)
        
        # Draw requirement plunder icons inside rectangle (evenly spaced)
        if offering.requirements:
            icon_size = config.OFFERING_STYLE['requirement_icon_size']
            
            # Collect all requirement icons
            req_icons = []
            for resource, amount in offering.requirements.items():
                icon_name = RESOURCE_ICONS.get(resource, resource)
                for _ in range(amount):
                    req_icons.append(icon_name)
            
            # Calculate spacing for even distribution
            num_icons = len(req_icons)
            if num_icons > 0:
                total_width = num_icons * icon_size
                spacing = max(2, (rect_width - total_width) // (num_icons + 1))
                
                icon_x = rect_x + spacing
                icon_y = center_y + 5
                
                for icon_name in req_icons:
                    icon = load_icon(icon_name, icon_size)
                    if icon:
                        screen.blit(icon, (icon_x, icon_y))
                    else:
                        # Fallback: colored squares
                        resource_colors = {
                            'livestock': config.BROWN,
                            'gold': config.GOLD,
                            'iron': config.DARK_GRAY,
                            'silver': config.LIGHT_GRAY
                        }
                        color = resource_colors.get(icon_name, config.BLACK)
                        pygame.draw.rect(screen, color, (icon_x, icon_y, icon_size, icon_size))
                        pygame.draw.rect(screen, config.BLACK, (icon_x, icon_y, icon_size, icon_size), 1)
                        icon_x += icon_size + spacing
    
    def get_hover_info(self, mouse_pos, state: GameState):
        """Get information about what the mouse is hovering over"""
        mx, my = mouse_pos
        
        # Check offerings on slots
        for i, offering in enumerate(state.visible_offerings[:len(config.OFFERING_SLOTS)]):
            if i < len(config.OFFERING_SLOTS):
                rel_x, rel_y = config.OFFERING_SLOTS[i]
                center_x = self.x + rel_x
                center_y = self.y + rel_y
                
                rect_width = config.OFFERING_STYLE['width']
                rect_height = config.OFFERING_STYLE['height']
                rect_x = center_x - rect_width // 2
                rect_y = center_y - rect_height // 2
                
                if (rect_x <= mx <= rect_x + rect_width and
                    rect_y <= my <= rect_y + rect_height):
                    return ('offering', offering)
        
        # Check buildings
        for building in self.board_db.buildings:
            if building.name in config.BUILDING_POSITIONS:
                rel_x, rel_y = config.BUILDING_POSITIONS[building.name]
                center_x = self.x + rel_x
                center_y = self.y + rel_y
                
                # Check if point is inside ellipse
                radius_x = config.BUILDING_STYLE['radius_x']
                radius_y = config.BUILDING_STYLE['radius_y']
                
                # Ellipse equation: ((x-cx)/rx)^2 + ((y-cy)/ry)^2 <= 1
                dx = (mx - center_x) / radius_x
                dy = (my - center_y) / radius_y
                if dx * dx + dy * dy <= 1:
                    return ('building', building)
        
        # Check raid sublocations
        for raid in self.board_db.raids:
            for subloc in raid.sublocations:
                if subloc.id in config.RAID_POSITIONS:
                    rel_x, rel_y = config.RAID_POSITIONS[subloc.id]
                    center_x = self.x + rel_x
                    center_y = self.y + rel_y
                    
                    rect_width = config.RAID_STYLE['width']
                    rect_height = config.RAID_STYLE['height']
                    rect_x = center_x - rect_width // 2
                    rect_y = center_y - rect_height // 2
                    
                    if (rect_x <= mx <= rect_x + rect_width and
                        rect_y <= my <= rect_y + rect_height):
                        # Get the raid state for this specific sublocation
                        subloc_state = next(
                            (rs for rs in state.raid_states 
                             if rs.location_id == raid.id and rs.sublocation_id == subloc.id),
                            None
                        )
                        return ('raid', {'raid': raid, 'sublocation': subloc, 'state': subloc_state})
        
        return None
