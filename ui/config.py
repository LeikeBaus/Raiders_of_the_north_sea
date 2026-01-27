"""
UI Configuration - All hardcoded values
"""
import pygame

# Window settings
WINDOW_WIDTH = 2560
WINDOW_HEIGHT = 1440
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
MARGIN = scale(10)  # Distance to edge and between views
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
DETAIL_VIEW_WIDTH = scale(300)
DETAIL_VIEW_HEIGHT = scale(400)
DETAIL_VIEW_PADDING = scale(10)
DETAIL_VIEW_BG = (240, 240, 240)
DETAIL_VIEW_BORDER = BLACK

# Board layout - 6-row grid system
# Each row height = board height / 6
ROW_HEIGHT = BOARD_VIEW_HEIGHT // 6
BOX_SPACING = scale(5)  # Space between boxes
SLOT_WIDTH = (BOARD_VIEW_WIDTH - 7 * BOX_SPACING) // 6  # Width for a single slot
SLOT_HEIGHT = scale(80)  # Height for raid/building slots

# Row 1: Fortresses (3 groups of 2 slots each: XX_XX_XX)
FORTRESS_Y = BOARD_VIEW_Y + BOX_SPACING
FORTRESS_SLOT_WIDTH = (BOARD_VIEW_WIDTH - 5 * BOX_SPACING) // 6  # 6 slots total

# Row 2: Monastery 2, Monastery 1, Outpost 2 (XX_XX_XX)
ROW2_Y = FORTRESS_Y + SLOT_HEIGHT + BOX_SPACING

# Row 3: Harbour 3, Outpost 1 (XXX_XX)
ROW3_Y = ROW2_Y + SLOT_HEIGHT + BOX_SPACING

# Row 4: Harbour 2, Harbour 1 (XXX_XXX)
ROW4_Y = ROW3_Y + SLOT_HEIGHT + BOX_SPACING

# Row 5: Buildings (left 2/3) + Offering 3 (right 1/3)
ROW5_Y = ROW4_Y + SLOT_HEIGHT + BOX_SPACING
BUILDING_AREA_WIDTH = (BOARD_VIEW_WIDTH * 2) // 3
BUILDING_SLOT_WIDTH = (BUILDING_AREA_WIDTH - 5 * BOX_SPACING) // 4

# Row 6: Buildings (left 2/3) + Offerings 1&2 (right 1/3)
ROW6_Y = ROW5_Y + SLOT_HEIGHT + BOX_SPACING

# Offering area (right 1/3 of rows 5 and 6)
OFFERING_AREA_X = BOARD_VIEW_X + BUILDING_AREA_WIDTH + BOX_SPACING
OFFERING_TILE_SIZE = scale(80)

# Building slot size
BUILDING_SLOT_HEIGHT = scale(80)

# Raid slot size
RAID_SLOT_WIDTH = scale(120)
RAID_SLOT_HEIGHT = SLOT_HEIGHT

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

# Cards - Detail view (larger)
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
