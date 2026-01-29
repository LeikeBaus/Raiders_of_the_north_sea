"""
Detail view - shows detailed information about hovered objects
"""
import pygame
from typing import Optional, Any
from pathlib import Path
from ui import config
from ui.components.icon_manager import load_icon, RESOURCE_ICONS, WORKER_ICONS


def _get_card_image_path(card_name: str) -> Optional[Path]:
    """Get the image path for a card by name"""
    filename = card_name.lower().replace(' ', '').replace("'", '') + '.jpg'
    image_path = Path(__file__).parent.parent.parent / 'res' / 'townsfolk' / filename
    if image_path.exists():
        return image_path
    return None


def _load_card_image(card_name: str, width: int, height: int) -> Optional[pygame.Surface]:
    """Load a card image"""
    image_path = _get_card_image_path(card_name)
    if image_path:
        try:
            image = pygame.image.load(str(image_path))
            image = pygame.transform.scale(image, (width, height))
            return image
        except Exception as e:
            print(f"Failed to load card image {image_path}: {e}")
    return None


class DetailView:
    """Shows detailed information about hovered objects"""
    
    def __init__(self):
        self.visible = False
        self.x = 0
        self.y = 0
        self.object_type = None  # 'card', 'building', 'raid', 'offering'
        self.object_data = None
        self.font_title = pygame.font.Font(None, config.scale(24))
        self.font_info = pygame.font.Font(None, config.scale(18))
        self.font_small = pygame.font.Font(None, config.scale(14))
    
    def show(self, x: int, y: int, object_type: str, object_data: Any):
        """Show detail view at position"""
        self.visible = True
        self.x = x
        self.y = y
        self.object_type = object_type
        self.object_data = object_data
    
    def hide(self):
        """Hide detail view"""
        self.visible = False
        self.object_data = None
    
    def draw(self, screen: pygame.Surface):
        """Draw detail view"""
        if not self.visible or not self.object_data:
            return
        
        # Use config sizes
        width = config.DETAIL_VIEW_WIDTH
        height = config.DETAIL_VIEW_HEIGHT
        
        x = self.x
        y = self.y
        
        # Keep on screen
        if x + width > config.WINDOW_WIDTH:
            x = config.WINDOW_WIDTH - width - 10
        if y + height > config.WINDOW_HEIGHT:
            y = config.WINDOW_HEIGHT - height - 10
        
        # Background
        pygame.draw.rect(screen, config.DETAIL_VIEW_BG, (x, y, width, height))
        pygame.draw.rect(screen, config.DETAIL_VIEW_BORDER, (x, y, width, height), 3)
        
        # Draw content based on type
        if self.object_type == 'card':
            self._draw_card_detail(screen, x, y, width, height)
        elif self.object_type == 'building':
            self._draw_building_detail(screen, x, y, width, height)
        elif self.object_type == 'raid':
            self._draw_raid_detail(screen, x, y, width, height)
        elif self.object_type == 'offering':
            self._draw_offering_detail(screen, x, y, width, height)
    
    def _draw_card_detail(self, screen: pygame.Surface, x: int, y: int, width: int, height: int):
        """Draw detailed card view"""
        card = self.object_data
        padding = config.DETAIL_VIEW_PADDING
        
        # Card visual (larger) - try to load image
        card_x = x + width // 2 - config.CARD_DETAIL_WIDTH // 2
        card_y = y + padding
        
        card_name = card.name if hasattr(card, 'name') else str(card)
        card_image = _load_card_image(card_name, config.CARD_DETAIL_WIDTH, config.CARD_DETAIL_HEIGHT)
        
        if card_image:
            screen.blit(card_image, (card_x, card_y))
        else:
            pygame.draw.rect(screen, config.WHITE, (card_x, card_y, config.CARD_DETAIL_WIDTH, config.CARD_DETAIL_HEIGHT))
            pygame.draw.rect(screen, config.BLACK, (card_x, card_y, config.CARD_DETAIL_WIDTH, config.CARD_DETAIL_HEIGHT), 2)
            
            name_surface = self.font_title.render(card_name, True, config.BLACK)
            screen.blit(name_surface, (card_x + 10, card_y + 10))
            
            cost = card.cost if hasattr(card, 'cost') else 0
            cost_text = self.font_info.render(f"Cost: {cost} Silver", True, config.BLUE)
            screen.blit(cost_text, (card_x + 10, card_y + 40))
            
            if hasattr(card, 'strength') and card.strength > 0:
                str_text = self.font_info.render(f"Strength: {card.strength}", True, config.RED)
                screen.blit(str_text, (card_x + 10, card_y + 70))
            
            if hasattr(card, 'vp') and card.vp > 0:
                vp_text = self.font_info.render(f"Victory Points: {card.vp}", True, config.GREEN)
                screen.blit(vp_text, (card_x + 10, card_y + 100))
            
            if hasattr(card, 'is_hero') and card.is_hero:
                hero_text = self.font_info.render("HERO", True, config.GOLD)
                screen.blit(hero_text, (card_x + 10, card_y + 130))
    
    def _draw_building_detail(self, screen: pygame.Surface, x: int, y: int, width: int, height: int):
        """Draw detailed building view"""
        building = self.object_data
        padding = config.DETAIL_VIEW_PADDING
        
        building_box_width = config.scale(200)
        building_box_height = config.scale(120)
        building_x = x + width // 2 - building_box_width // 2
        building_y = y + padding
        
        pygame.draw.rect(screen, config.DARK_GREEN, (building_x, building_y, building_box_width, building_box_height))
        pygame.draw.rect(screen, config.BLACK, (building_x, building_y, building_box_width, building_box_height), 3)
        
        title = building.name if hasattr(building, 'name') else str(building)
        title_surface = self.font_title.render(title, True, config.WHITE)
        title_rect = title_surface.get_rect(center=(building_x + building_box_width // 2, building_y + building_box_height // 2))
        screen.blit(title_surface, title_rect)
        
        details_y = building_y + building_box_height + 20
        
        if hasattr(building, 'worker_slots'):
            slots_text = self.font_info.render(f"Worker Slots: {building.worker_slots}", True, config.DARK_GRAY)
            screen.blit(slots_text, (x + padding, details_y))
            details_y += 30
        
        if hasattr(building, 'worker_requirement') and building.worker_requirement:
            req_text = "Allowed: " + ", ".join(building.worker_requirement)
            req_surface = self.font_small.render(req_text, True, config.DARK_BLUE)
            screen.blit(req_surface, (x + padding, details_y))
        else:
            req_surface = self.font_small.render("Allowed: Any worker", True, config.DARK_GREEN)
            screen.blit(req_surface, (x + padding, details_y))
        details_y += 35
        
        if hasattr(building, 'action'):
            action_title = self.font_info.render("Action:", True, config.BLACK)
            screen.blit(action_title, (x + padding, details_y))
            details_y += 30
            
            action_data = building.action
            desc = action_data.get('description', 'No description')
            
            words = desc.split()
            line = ""
            line_y = details_y
            for word in words:
                test_line = line + word + " "
                if self.font_small.size(test_line)[0] < width - 2 * padding:
                    line = test_line
                else:
                    if line:
                        text_surface = self.font_small.render(line, True, config.DARK_GRAY)
                        screen.blit(text_surface, (x + padding, line_y))
                        line_y += 20
                    line = word + " "
            
            if line:
                text_surface = self.font_small.render(line, True, config.DARK_GRAY)
                screen.blit(text_surface, (x + padding, line_y))
    
    def _draw_raid_detail(self, screen: pygame.Surface, x: int, y: int, width: int, height: int):
        """Draw detailed raid location view"""
        if isinstance(self.object_data, dict):
            raid = self.object_data.get('raid')
            subloc = self.object_data.get('sublocation')
            subloc_state = self.object_data.get('state')
        else:
            raid = self.object_data
            subloc = None
            subloc_state = None
        
        padding = config.DETAIL_VIEW_PADDING
        
        color_map = {
            'harbour': config.BLUE,
            'harbor': config.BLUE,
            'outpost': config.ORANGE,
            'monastery': config.PURPLE,
            'fortress': config.RED
        }
        raid_color = color_map.get(raid.type, config.GRAY)
        
        raid_box_width = config.scale(200)
        raid_box_height = config.scale(80)
        raid_x = x + width // 2 - raid_box_width // 2
        raid_y = y + padding
        
        pygame.draw.rect(screen, raid_color, (raid_x, raid_y, raid_box_width, raid_box_height))
        pygame.draw.rect(screen, config.BLACK, (raid_x, raid_y, raid_box_width, raid_box_height), 3)
        
        title = raid.name if hasattr(raid, 'name') else str(raid)
        title_surface = self.font_title.render(title, True, config.WHITE)
        title_rect = title_surface.get_rect(center=(raid_x + raid_box_width // 2, raid_y + 25))
        screen.blit(title_surface, title_rect)
        
        type_text = raid.type.upper()
        type_surface = self.font_small.render(type_text, True, config.WHITE)
        type_rect = type_surface.get_rect(center=(raid_x + raid_box_width // 2, raid_y + 55))
        screen.blit(type_surface, type_rect)
        
        details_y = raid_y + raid_box_height + 15
        icon_size = 18
        
        # Requirements section
        if hasattr(raid, 'requirements'):
            req = raid.requirements
            min_crew = req.get('min_crew', 0) if isinstance(req, dict) else getattr(req, 'min_crew', 0)
            provisions = req.get('provisions', 0) if isinstance(req, dict) else getattr(req, 'provisions', 0)
            gold_cost = req.get('gold', 0) if isinstance(req, dict) else getattr(req, 'gold', 0)
            
            text = self.font_info.render(f"Min Crew: {min_crew}", True, config.BLACK)
            screen.blit(text, (x + padding, details_y))
            details_y += 25
            
            if provisions > 0 or gold_cost > 0:
                cost_text = self.font_info.render("Costs:", True, config.BLACK)
                screen.blit(cost_text, (x + padding, details_y))
                details_y += 22
                
                if provisions > 0:
                    icon = load_icon(RESOURCE_ICONS['provisions'], icon_size)
                    if icon:
                        screen.blit(icon, (x + padding + 10, details_y))
                        text = self.font_small.render(f"x{provisions}", True, config.DARK_GRAY)
                        screen.blit(text, (x + padding + 32, details_y + 2))
                    details_y += 22
                
                if gold_cost > 0:
                    icon = load_icon(RESOURCE_ICONS['gold'], icon_size)
                    if icon:
                        screen.blit(icon, (x + padding + 10, details_y))
                        text = self.font_small.render(f"x{gold_cost}", True, config.DARK_GRAY)
                        screen.blit(text, (x + padding + 32, details_y + 2))
                    details_y += 22
            else:
                cost_text = self.font_small.render("Costs: None", True, config.DARK_GREEN)
                screen.blit(cost_text, (x + padding, details_y))
                details_y += 25
        
        # Dice bonus
        if hasattr(raid, 'dice_added'):
            dice_icon = load_icon(RESOURCE_ICONS['dice'], 20)
            if dice_icon:
                screen.blit(dice_icon, (x + padding, details_y))
                dice_text = self.font_info.render(f"Dice: +{raid.dice_added}d6", True, config.BLACK)
                screen.blit(dice_text, (x + padding + 25, details_y + 2))
            else:
                dice_text = self.font_info.render(f"Dice: +{raid.dice_added}d6", True, config.BLACK)
                screen.blit(dice_text, (x + padding, details_y))
            details_y += 30
        
        # Plunder for this specific sublocation
        if subloc_state and subloc_state.plunder_resources:
            plunder_title = self.font_info.render("Plunder:", True, config.BLACK)
            screen.blit(plunder_title, (x + padding, details_y))
            details_y += 22
            
            for resource, count in sorted(subloc_state.plunder_resources.items()):
                icon = load_icon(RESOURCE_ICONS.get(resource, 'gold'), icon_size)
                if icon:
                    screen.blit(icon, (x + padding + 10, details_y))
                    text = self.font_small.render(f"x{count}", True, config.DARK_GRAY)
                    screen.blit(text, (x + padding + 32, details_y + 2))
                details_y += 22
        elif subloc_state:
            plunder_text = self.font_small.render("Plunder: None", True, config.DARK_RED)
            screen.blit(plunder_text, (x + padding, details_y))
            details_y += 25
        
        # VP Tiers
        if hasattr(raid, 'vp_tiers') and raid.vp_tiers:
            details_y += 5
            vp_title = self.font_info.render("VP Tiers:", True, config.BLACK)
            screen.blit(vp_title, (x + padding, details_y))
            details_y += 22
            
            sorted_tiers = sorted(raid.vp_tiers, key=lambda t: t.min_strength, reverse=True)
            for tier in sorted_tiers:
                tier_text = f"  {tier.min_strength}+ Strength → {tier.vp} VP"
                text_surface = self.font_small.render(tier_text, True, config.DARK_GRAY)
                screen.blit(text_surface, (x + padding + 10, details_y))
                details_y += 20
    
    def _draw_offering_detail(self, screen: pygame.Surface, x: int, y: int, width: int, height: int):
        """Draw detailed offering tile view"""
        offering = self.object_data
        padding = config.DETAIL_VIEW_PADDING
        
        tile_size = config.scale(150)
        tile_x = x + width // 2 - tile_size // 2
        tile_y = y + padding
        
        pygame.draw.rect(screen, config.GOLD, (tile_x, tile_y, tile_size, tile_size))
        pygame.draw.rect(screen, config.BLACK, (tile_x, tile_y, tile_size, tile_size), 3)
        
        vp_icon = load_icon(RESOURCE_ICONS['vp'], config.scale(40))
        if vp_icon:
            icon_x = tile_x + tile_size // 2 - config.scale(20)
            screen.blit(vp_icon, (icon_x, tile_y + 20))
        
        vp_text = f"{offering.vp}"
        vp_surface = self.font_title.render(vp_text, True, config.BLACK)
        vp_rect = vp_surface.get_rect(center=(tile_x + tile_size // 2, tile_y + 80))
        screen.blit(vp_surface, vp_rect)
        
        type_surface = self.font_small.render("Victory Points", True, config.BLACK)
        type_rect = type_surface.get_rect(center=(tile_x + tile_size // 2, tile_y + 110))
        screen.blit(type_surface, type_rect)
        
        details_y = tile_y + tile_size + 20
        
        if hasattr(offering, 'requirements'):
            req_title = self.font_info.render("Cost:", True, config.BLACK)
            screen.blit(req_title, (x + padding, details_y))
            
            req_y = details_y + 30
            icon_size = 20
            for resource, amount in offering.requirements.items():
                icon_name = RESOURCE_ICONS.get(resource, resource)
                icon = load_icon(icon_name, icon_size)
                if icon:
                    screen.blit(icon, (x + padding + 10, req_y))
                    text = self.font_small.render(f"x {amount}", True, config.DARK_GRAY)
                    screen.blit(text, (x + padding + 35, req_y + 2))
                else:
                    text = self.font_small.render(f"{resource.capitalize()}: {amount}", True, config.DARK_GRAY)
                    screen.blit(text, (x + padding + 10, req_y))
                req_y += 25
