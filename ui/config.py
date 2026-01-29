"""
UI Configuration - All hardcoded values
"""
import pygame

# Window settings
WINDOW_WIDTH = 2560 # 2560
WINDOW_HEIGHT = 1400 # 1440
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
DETAIL_VIEW_WIDTH = WINDOW_WIDTH * 0.15
DETAIL_VIEW_HEIGHT = WINDOW_HEIGHT * 0.35
DETAIL_VIEW_PADDING = WINDOW_HEIGHT // 100
DETAIL_VIEW_BG = (240, 240, 240)
DETAIL_VIEW_BORDER = BLACK

# Player view
PLAYER_PANEL_HEIGHT = PLAYER_VIEW_WIDTH * 0.15
PLAYER_PANEL_MARGIN = PLAYER_PANEL_HEIGHT * 0.01
PLAYER_NAME_FONT_SIZE = PLAYER_PANEL_HEIGHT * 0.02
PLAYER_INFO_FONT_SIZE = PLAYER_PANEL_HEIGHT * 0.02

# Cards
CARD_WIDTH = PLAYER_VIEW_WIDTH * 0.1
CARD_HEIGHT = PLAYER_PANEL_HEIGHT * 1.4
CARD_SPACING = PLAYER_VIEW_WIDTH * 0.005
CARD_FONT_SIZE = int(PLAYER_VIEW_WIDTH * 0.015)

# Cards - Detail view
CARD_DETAIL_WIDTH = DETAIL_VIEW_WIDTH * 0.9
CARD_DETAIL_HEIGHT = DETAIL_VIEW_HEIGHT * 0.93

# Resources
RESOURCE_ICON_SIZE = PLAYER_PANEL_HEIGHT * 0.5
RESOURCE_SPACING = PLAYER_PANEL_HEIGHT
RESOURCE_FONT_SIZE = int(PLAYER_PANEL_HEIGHT * 0.5)

# Actions
ACTION_ITEM_HEIGHT = ACTION_PANEL_HEIGHT * 0.1
ACTION_FONT_SIZE = int(ACTION_PANEL_HEIGHT* 0.1)
ACTIONS_PER_PAGE = 8

# Buttons
BUTTON_HEIGHT = WINDOW_HEIGHT * 0.1
BUTTON_FONT_SIZE = int(WINDOW_HEIGHT * 0.04)
BUTTON_PADDING = int(WINDOW_HEIGHT * 0.04)

# Coordinate-based Board Layout System
# ====================================

# Raid Location Style (white rectangle, 60% transparency)
RAID_STYLE = {
    'color': (255, 255, 255),  # White
    'alpha': 51,  # 20% of 255
    'width': BOARD_VIEW_WIDTH * 0.094,
    'height': BOARD_VIEW_HEIGHT * 0.065,
    'border_width': 2,
    'border_color': WHITE,
    'plunder_icon_size': BOARD_VIEW_WIDTH * 0.027,
    'worker_icon_size': BOARD_VIEW_WIDTH * 0.04
}

# Village Building Style (white ellipse, 60% transparency)
BUILDING_STYLE = {
    'color': (255, 255, 255),  # White
    'alpha': 153,  # 60% of 255
    'radius_x': BOARD_VIEW_WIDTH * 0.021,  # Horizontal radius
    'radius_y': BOARD_VIEW_HEIGHT * 0.008,  # Vertical radius
    'border_width': 2,
    'border_color': WHITE,
    'worker_icon_size': BOARD_VIEW_WIDTH * 0.05
}

# Offering Style (red rectangle, 60% transparency)
OFFERING_STYLE = {
    'color': (220, 50, 50),  # Red
    'alpha': 153,  # 60% of 255
    'width': BOARD_VIEW_WIDTH * 0.094,
    'height': BOARD_VIEW_HEIGHT * 0.078,
    'border_width': 2,
    'border_color': WHITE,
    'requirement_icon_size': int(BOARD_VIEW_WIDTH * 0.018),
    'vp_font_size': int(BOARD_VIEW_WIDTH * 0.016)
}

# Middle point coordinates for all raid sublocations (x, y relative to BOARD_VIEW)
# Format: 'sublocation_id': (x, y)
RAID_POSITIONS = {
    # Harbour 1 (3 sublocations)
    'harbour1_sub1': (BOARD_VIEW_WIDTH * 0.620, BOARD_VIEW_HEIGHT * 0.59),
    'harbour1_sub2': (BOARD_VIEW_WIDTH * 0.753, BOARD_VIEW_HEIGHT * 0.582),
    'harbour1_sub3': (BOARD_VIEW_WIDTH * 0.888, BOARD_VIEW_HEIGHT * 0.577),
    
    # Harbour 2 (3 sublocations)
    'harbour2_sub1': (BOARD_VIEW_WIDTH * 0.370, BOARD_VIEW_HEIGHT * 0.477),
    'harbour2_sub2': (BOARD_VIEW_WIDTH * 0.504, BOARD_VIEW_HEIGHT * 0.473),
    'harbour2_sub3': (BOARD_VIEW_WIDTH * 0.638, BOARD_VIEW_HEIGHT * 0.467),
    
    # Harbour 3 (3 sublocations)
    'harbour3_sub1': (BOARD_VIEW_WIDTH * 0.117, BOARD_VIEW_HEIGHT * 0.366),
    'harbour3_sub2': (BOARD_VIEW_WIDTH * 0.250, BOARD_VIEW_HEIGHT * 0.361),
    'harbour3_sub3': (BOARD_VIEW_WIDTH * 0.385, BOARD_VIEW_HEIGHT * 0.356),
    
    # Outpost 1 (2 sublocations)
    'outpost1_sub1': (BOARD_VIEW_WIDTH * 0.752, BOARD_VIEW_HEIGHT * 0.36),
    'outpost1_sub2': (BOARD_VIEW_WIDTH * 0.887, BOARD_VIEW_HEIGHT * 0.365),
    
    # Outpost 2 (2 sublocations)
    'outpost2_sub1': (BOARD_VIEW_WIDTH * 0.567, BOARD_VIEW_HEIGHT * 0.22),
    'outpost2_sub2': (BOARD_VIEW_WIDTH * 0.434, BOARD_VIEW_HEIGHT * 0.215),
    
    # Monastery 1 (2 sublocations)
    'monastery1_sub1': (BOARD_VIEW_WIDTH * 0.118, BOARD_VIEW_HEIGHT * 0.213),
    'monastery1_sub2': (BOARD_VIEW_WIDTH * 0.25, BOARD_VIEW_HEIGHT * 0.205),
    
    # Monastery 2 (2 sublocations)
    'monastery2_sub1': (BOARD_VIEW_WIDTH * 0.884, BOARD_VIEW_HEIGHT * 0.21),
    'monastery2_sub2': (BOARD_VIEW_WIDTH * 0.75, BOARD_VIEW_HEIGHT * 0.215),
    
    # Fortress 1 (2 sublocations)
    'fortress1_sub1': (BOARD_VIEW_WIDTH * 0.12, BOARD_VIEW_HEIGHT * 0.0667),
    'fortress1_sub2': (BOARD_VIEW_WIDTH * 0.253, BOARD_VIEW_HEIGHT * 0.0667),
    
    # Fortress 2 (2 sublocations)
    'fortress2_sub1': (BOARD_VIEW_WIDTH * 0.434, BOARD_VIEW_HEIGHT * 0.0667),
    'fortress2_sub2': (BOARD_VIEW_WIDTH * 0.566, BOARD_VIEW_HEIGHT * 0.0667),
    
    # Fortress 3 (2 sublocations)
    'fortress3_sub1': (BOARD_VIEW_WIDTH * 0.748, BOARD_VIEW_HEIGHT * 0.0667),
    'fortress3_sub2': (BOARD_VIEW_WIDTH * 0.879, BOARD_VIEW_HEIGHT * 0.0667),
}

# Middle point coordinates for all village buildings (x, y relative to BOARD_VIEW)
# Format: 'building_name': (x, y)
BUILDING_POSITIONS = {
    'Gate House': (BOARD_VIEW_WIDTH * 0.192, BOARD_VIEW_HEIGHT * 0.663),
    'Treasury': (BOARD_VIEW_WIDTH * 0.199, BOARD_VIEW_HEIGHT * 0.765),
    'Town Hall': (BOARD_VIEW_WIDTH * 0.303, BOARD_VIEW_HEIGHT * 0.721),
    'Barracks': (BOARD_VIEW_WIDTH * 0.446, BOARD_VIEW_HEIGHT * 0.758),
    'Armoury': (BOARD_VIEW_WIDTH * 0.212, BOARD_VIEW_HEIGHT * 0.873),
    'Mill': (BOARD_VIEW_WIDTH * 0.316, BOARD_VIEW_HEIGHT * 0.841),
    'Silversmith': (BOARD_VIEW_WIDTH * 0.463, BOARD_VIEW_HEIGHT * 0.866),
    'Long House': (BOARD_VIEW_WIDTH * 0.635, BOARD_VIEW_HEIGHT * 0.8715),
}

# Offering slots - middle point coordinates (x, y relative to BOARD_VIEW)
# Offerings are placed on these slots based on availability
# Format: list of (x, y) tuples for each slot
OFFERING_SLOTS = [
    (BOARD_VIEW_WIDTH * 0.692, BOARD_VIEW_HEIGHT * 0.94),  # Slot 0
    (BOARD_VIEW_WIDTH * 0.812, BOARD_VIEW_HEIGHT * 0.94),  # Slot 1
    (BOARD_VIEW_WIDTH * 0.934, BOARD_VIEW_HEIGHT * 0.94),  # Slot 2
]

# Fonts (initialized in main)
FONT_LARGE = None
FONT_MEDIUM = None
FONT_SMALL = None
FONT_TINY = None


def init_fonts():
    """Initialize pygame fonts"""
    global FONT_LARGE, FONT_MEDIUM, FONT_SMALL, FONT_TINY
    FONT_LARGE = pygame.font.Font(None, int(WINDOW_WIDTH * 0.02))
    FONT_MEDIUM = pygame.font.Font(None, int(WINDOW_WIDTH * 0.015))
    FONT_SMALL = pygame.font.Font(None, int(WINDOW_WIDTH * 0.01))
    FONT_TINY = pygame.font.Font(None, int(WINDOW_WIDTH * 0.008))