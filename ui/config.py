"""
UI Configuration - All hardcoded values
"""
import pygame

# Window settings
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 1000
FPS = 60
TITLE = "Raiders of the North Sea"

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

# Layout - Main Game Screen
BOARD_VIEW_X = 20
BOARD_VIEW_Y = 20
BOARD_VIEW_WIDTH = 900
BOARD_VIEW_HEIGHT = 960

PLAYER_VIEW_X = 940
PLAYER_VIEW_Y = 20
PLAYER_VIEW_WIDTH = 640
PLAYER_VIEW_HEIGHT = 500

ACTION_PANEL_X = 940
ACTION_PANEL_Y = 540
ACTION_PANEL_WIDTH = 640
ACTION_PANEL_HEIGHT = 440

# Board layout (simplified from board image)
# Village buildings (bottom-left area)
VILLAGE_AREA_X = 50
VILLAGE_AREA_Y = 600
VILLAGE_BUILDING_WIDTH = 120
VILLAGE_BUILDING_HEIGHT = 80
VILLAGE_BUILDING_SPACING = 20

# Raid locations (top-right area)
RAID_AREA_X = 500
RAID_AREA_Y = 50
RAID_LOCATION_WIDTH = 150
RAID_LOCATION_HEIGHT = 100
RAID_LOCATION_SPACING = 20

# Offering tiles area
OFFERING_AREA_X = 350
OFFERING_AREA_Y = 650
OFFERING_TILE_SIZE = 60

# Building positions (based on board image layout)
BUILDING_POSITIONS = {
    "Gate House": (50, 650),
    "Town Hall": (200, 700),
    "Treasury": (50, 800),
    "Barracks": (350, 750),
    "Armoury": (50, 900),
    "Mill": (200, 850),
    "Silversmith": (350, 900),
    "Long House": (500, 800),
}

# Raid location positions (harbors, outposts, monasteries, fortresses)
RAID_POSITIONS = {
    "Harbour": [(500, 50), (650, 100), (500, 200)],  # 3 harbor locations
    "Outpost": [(650, 250), (750, 300)],             # 2 outpost locations
    "Monastery": [(600, 400), (750, 450)],           # 2 monastery locations
    "Fortress": [(550, 550), (700, 600), (650, 700)], # 3 fortress locations
}

# Player view
PLAYER_PANEL_HEIGHT = 120
PLAYER_PANEL_MARGIN = 10
PLAYER_NAME_FONT_SIZE = 24
PLAYER_INFO_FONT_SIZE = 16

# Cards
CARD_WIDTH = 80
CARD_HEIGHT = 110
CARD_SPACING = 5
CARD_FONT_SIZE = 12

# Resources
RESOURCE_ICON_SIZE = 30
RESOURCE_SPACING = 5
RESOURCE_FONT_SIZE = 16

# Actions
ACTION_ITEM_HEIGHT = 30
ACTION_FONT_SIZE = 16
ACTIONS_PER_PAGE = 12

# Buttons
BUTTON_HEIGHT = 50
BUTTON_FONT_SIZE = 24
BUTTON_PADDING = 10

# Fonts (initialized in main)
FONT_LARGE = None
FONT_MEDIUM = None
FONT_SMALL = None
FONT_TINY = None


def init_fonts():
    """Initialize pygame fonts"""
    global FONT_LARGE, FONT_MEDIUM, FONT_SMALL, FONT_TINY
    FONT_LARGE = pygame.font.Font(None, 48)
    FONT_MEDIUM = pygame.font.Font(None, 32)
    FONT_SMALL = pygame.font.Font(None, 24)
    FONT_TINY = pygame.font.Font(None, 18)
