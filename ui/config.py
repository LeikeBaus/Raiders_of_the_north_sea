"""
UI Configuration - All hardcoded values
"""
import pygame

# Window settings
WINDOW_WIDTH = 2736 # 2560
WINDOW_HEIGHT = 1624 # 1440
FPS = 60
TITLE = "Raiders of the North Sea"

# Base resolution for scaling (original design)
BASE_WIDTH = 2560
BASE_HEIGHT = 1440

# Calculate scale factor based on current resolution
SCALE_X = WINDOW_WIDTH / BASE_WIDTH
SCALE_Y = WINDOW_HEIGHT / BASE_HEIGHT
SCALE = min(SCALE_X, SCALE_Y)  # Use uniform scaling

def scale(value):
    """Scale a value by the current scale factor"""
    return int(value * SCALE)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
RED = (220, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 100, 200)
YELLOW = (255, 200, 50)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)
DARK_GREEN = (34, 139, 34)
DARK_BLUE = (25, 25, 112)
PURPLE = (128, 0, 128)
ORANGE = (255, 140, 0)

# Layout - Main Game Screen with margins
MARGIN = WINDOW_HEIGHT // 100  # Distance to edge and between views
HALF_WIDTH = WINDOW_WIDTH // 2

# Left half: Board view
BOARD_VIEW_X = MARGIN
BOARD_VIEW_Y = MARGIN
BOARD_VIEW_WIDTH = HALF_WIDTH - 2 * MARGIN
BOARD_VIEW_HEIGHT = WINDOW_HEIGHT - 2 * MARGIN

# Right half: Player view (upper 2/3), Action and History (lower 1/3 split)
RIGHT_SIDE_X = HALF_WIDTH + MARGIN
RIGHT_SIDE_WIDTH = HALF_WIDTH - 2 * MARGIN
LOWER_THIRD_HEIGHT = (WINDOW_HEIGHT - 3 * MARGIN) // 3

PLAYER_VIEW_X = RIGHT_SIDE_X
PLAYER_VIEW_Y = MARGIN
PLAYER_VIEW_WIDTH = RIGHT_SIDE_WIDTH
PLAYER_VIEW_HEIGHT = 2 * LOWER_THIRD_HEIGHT

ACTION_PANEL_X = RIGHT_SIDE_X
ACTION_PANEL_Y = PLAYER_VIEW_Y + PLAYER_VIEW_HEIGHT + MARGIN
ACTION_PANEL_WIDTH = RIGHT_SIDE_WIDTH // 2 - MARGIN
ACTION_PANEL_HEIGHT = LOWER_THIRD_HEIGHT

HISTORY_PANEL_X = ACTION_PANEL_X + ACTION_PANEL_WIDTH + MARGIN
HISTORY_PANEL_Y = ACTION_PANEL_Y
HISTORY_PANEL_WIDTH = RIGHT_SIDE_WIDTH // 2 - MARGIN
HISTORY_PANEL_HEIGHT = LOWER_THIRD_HEIGHT

# Detail view (hover tooltip)
DETAIL_VIEW_WIDTH = WINDOW_WIDTH // 8
DETAIL_VIEW_HEIGHT = WINDOW_HEIGHT // 3
DETAIL_VIEW_PADDING = WINDOW_HEIGHT // 100
DETAIL_VIEW_BG = (240, 240, 240)
DETAIL_VIEW_BORDER = BLACK

# Worker icon size
WORKER_ICON_SIZE = scale(20)

# Player view
PLAYER_PANEL_HEIGHT = scale(120)
PLAYER_PANEL_MARGIN = scale(10)
PLAYER_NAME_FONT_SIZE = scale(24)
PLAYER_INFO_FONT_SIZE = scale(16)

# Cards
CARD_WIDTH = scale(80)
CARD_HEIGHT = scale(110)
CARD_SPACING = scale(5)
CARD_FONT_SIZE = scale(12)

# Cards - Detail view
CARD_DETAIL_WIDTH = scale(240)
CARD_DETAIL_HEIGHT = scale(330)
CARD_DETAIL_FONT_NAME = scale(20)
CARD_DETAIL_FONT_INFO = scale(16)

# Resources
RESOURCE_ICON_SIZE = scale(30)
RESOURCE_SPACING = scale(5)
RESOURCE_FONT_SIZE = scale(16)

# Actions
ACTION_ITEM_HEIGHT = scale(30)
ACTION_FONT_SIZE = scale(16)
ACTIONS_PER_PAGE = 12

# Buttons
BUTTON_HEIGHT = scale(50)
BUTTON_FONT_SIZE = scale(24)
BUTTON_PADDING = scale(10)

# Coordinate-based Board Layout System
# ====================================

# Raid Location Style (white rectangle, 60% transparency)
RAID_STYLE = {
    'color': (255, 255, 255),  # White
    'alpha': 51,  # 20% of 255
    'width': scale(120),
    'height': scale(90),
    'border_width': 2,
    'border_color': WHITE,
    'plunder_icon_size': scale(40),
    'worker_icon_size': scale(50)
}

# Village Building Style (white ellipse, 60% transparency)
BUILDING_STYLE = {
    'color': (255, 255, 255),  # White
    'alpha': 153,  # 60% of 255
    'radius_x': scale(50),  # Horizontal radius
    'radius_y': scale(40),  # Vertical radius
    'border_width': 2,
    'border_color': WHITE,
    'worker_icon_size': scale(25)
}

# Offering Style (red rectangle, 60% transparency)
OFFERING_STYLE = {
    'color': (220, 50, 50),  # Red
    'alpha': 153,  # 60% of 255
    'width': scale(90),
    'height': scale(70),
    'border_width': 2,
    'border_color': WHITE,
    'requirement_icon_size': scale(18),
    'vp_font_size': scale(16)
}

# Middle point coordinates for all raid sublocations (x, y relative to BOARD_VIEW)
# Format: 'sublocation_id': (x, y)
RAID_POSITIONS = {
    # Harbour 1 (3 sublocations)
    'harbour1_sub1': (BOARD_VIEW_WIDTH * 5 // 8 - scale(10), BOARD_VIEW_HEIGHT * 5 // 8 - scale(54)),
    'harbour1_sub2': (BOARD_VIEW_WIDTH * 6 // 8 + scale(4), BOARD_VIEW_HEIGHT * 5 // 8 - scale(63)),
    'harbour1_sub3': (BOARD_VIEW_WIDTH * 7 // 8 + scale(14), BOARD_VIEW_HEIGHT * 5 // 8 - scale(72)),
    
    # Harbour 2 (3 sublocations)
    'harbour2_sub1': (BOARD_VIEW_WIDTH * 3 // 8 - scale(5), BOARD_VIEW_HEIGHT * 1 // 2 - scale(37)),
    'harbour2_sub2': (BOARD_VIEW_WIDTH * 4 // 8 + scale(6), BOARD_VIEW_HEIGHT * 1 // 2 - scale(44)),
    'harbour2_sub3': (BOARD_VIEW_WIDTH * 5 // 8 + scale(16), BOARD_VIEW_HEIGHT * 1 // 2 - scale(51)),
    
    # Harbour 3 (3 sublocations)
    'harbour3_sub1': (BOARD_VIEW_WIDTH * 1 // 8 - scale(12), BOARD_VIEW_HEIGHT * 1 // 3 + scale(50)),
    'harbour3_sub2': (BOARD_VIEW_WIDTH * 2 // 8, BOARD_VIEW_HEIGHT * 1 // 3 + scale(43)),
    'harbour3_sub3': (BOARD_VIEW_WIDTH * 3 // 8 + scale(12), BOARD_VIEW_HEIGHT * 1 // 3 + scale(36)),
    
    # Outpost 1 (2 sublocations)
    'outpost1_sub1': (BOARD_VIEW_WIDTH * 6 // 8 + scale(2), BOARD_VIEW_HEIGHT * 2 // 6 + scale(37)),
    'outpost1_sub2': (BOARD_VIEW_WIDTH * 7 // 8 + scale(16), BOARD_VIEW_HEIGHT * 2 // 6 + scale(44)),
    
    # Outpost 2 (2 sublocations)
    'outpost2_sub1': (BOARD_VIEW_WIDTH * 5 // 8 - scale(71), BOARD_VIEW_HEIGHT * 1 // 5 + scale(25)),
    'outpost2_sub2': (BOARD_VIEW_WIDTH * 3 // 8 + scale(75), BOARD_VIEW_HEIGHT * 1 // 5 + scale(20)),
    
    # Monastery 1 (2 sublocations)
    'monastery1_sub1': (BOARD_VIEW_WIDTH * 1 // 8 - scale(8), BOARD_VIEW_HEIGHT * 1 // 5 + scale(12)),
    'monastery1_sub2': (BOARD_VIEW_WIDTH * 2 // 8 + scale(4), BOARD_VIEW_HEIGHT * 1 // 5 + scale(8)),
    
    # Monastery 2 (2 sublocations)
    'monastery2_sub1': (BOARD_VIEW_WIDTH * 7 // 8 + scale(12), BOARD_VIEW_HEIGHT * 1 // 5 + scale(10)),
    'monastery2_sub2': (BOARD_VIEW_WIDTH * 6 // 8, BOARD_VIEW_HEIGHT * 1 // 5 + scale(12)),
    
    # Fortress 1 (2 sublocations)
    'fortress1_sub1': (BOARD_VIEW_WIDTH * 1 // 8 - scale(8), BOARD_VIEW_HEIGHT * 1 // 15),
    'fortress1_sub2': (BOARD_VIEW_WIDTH * 2 // 8 + scale(4), BOARD_VIEW_HEIGHT * 1 // 15),
    
    # Fortress 2 (2 sublocations)
    'fortress2_sub1': (BOARD_VIEW_WIDTH * 3 // 8 + scale(72), BOARD_VIEW_HEIGHT * 1 // 15),
    'fortress2_sub2': (BOARD_VIEW_WIDTH * 5 // 8 - scale(72), BOARD_VIEW_HEIGHT * 1 // 15),
    
    # Fortress 3 (2 sublocations)
    'fortress3_sub1': (BOARD_VIEW_WIDTH * 6 // 8, BOARD_VIEW_HEIGHT * 1 // 15),
    'fortress3_sub2': (BOARD_VIEW_WIDTH * 7 // 8 + scale(8), BOARD_VIEW_HEIGHT * 1 // 15),
}

# Middle point coordinates for all village buildings (x, y relative to BOARD_VIEW)
# Format: 'building_name': (x, y)
BUILDING_POSITIONS = {
    'Gate House': (BOARD_VIEW_WIDTH * 1 // 9, BOARD_VIEW_HEIGHT * 5 // 6),
    'Treasury': (BOARD_VIEW_WIDTH * 2 // 9, BOARD_VIEW_HEIGHT * 5 // 6),
    'Town Hall': (BOARD_VIEW_WIDTH * 3 // 9, BOARD_VIEW_HEIGHT * 5 // 6),
    'Barracks': (BOARD_VIEW_WIDTH * 4 // 9, BOARD_VIEW_HEIGHT * 5 // 6),
    'Armoury': (BOARD_VIEW_WIDTH * 1 // 9, BOARD_VIEW_HEIGHT * 6 // 6 - scale(40)),
    'Mill': (BOARD_VIEW_WIDTH * 2 // 9, BOARD_VIEW_HEIGHT * 6 // 6 - scale(40)),
    'Silversmith': (BOARD_VIEW_WIDTH * 3 // 9, BOARD_VIEW_HEIGHT * 6 // 6 - scale(40)),
    'Long House': (BOARD_VIEW_WIDTH * 4 // 9, BOARD_VIEW_HEIGHT * 6 // 6 - scale(40)),
}

# Offering slots - middle point coordinates (x, y relative to BOARD_VIEW)
# Offerings are placed on these slots based on availability
# Format: list of (x, y) tuples for each slot
OFFERING_SLOTS = [
    (BOARD_VIEW_WIDTH * 7 // 8, BOARD_VIEW_HEIGHT * 5 // 6),  # Slot 0
    (BOARD_VIEW_WIDTH * 6 // 8, BOARD_VIEW_HEIGHT * 6 // 6 - scale(40)),  # Slot 1
    (BOARD_VIEW_WIDTH * 7 // 8, BOARD_VIEW_HEIGHT * 6 // 6 - scale(40)),  # Slot 2
]

# Fonts (initialized in main)
FONT_LARGE = None
FONT_MEDIUM = None
FONT_SMALL = None
FONT_TINY = None


def init_fonts():
    """Initialize pygame fonts"""
    global FONT_LARGE, FONT_MEDIUM, FONT_SMALL, FONT_TINY
    FONT_LARGE = pygame.font.Font(None, scale(48))
    FONT_MEDIUM = pygame.font.Font(None, scale(32))
    FONT_SMALL = pygame.font.Font(None, scale(24))
    FONT_TINY = pygame.font.Font(None, scale(18))
