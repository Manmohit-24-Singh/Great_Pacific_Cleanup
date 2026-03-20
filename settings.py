# settings.py

# Display
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 800
FPS = 60
TITLE = "Great Pacific Cleanup"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
UI_BG = (10, 15, 30, 200)

# Ocean palette (deep layered blues)
OCEAN_DEEP = (5, 25, 55)
OCEAN_MID = (8, 45, 85)
OCEAN_LIGHT = (15, 70, 120)
OCEAN_SURFACE = (20, 100, 155)
OCEAN_FOAM = (180, 220, 240)
OCEAN_HIGHLIGHT = (100, 180, 220)

# Colors – Entities
PLASTIC_COLOR = (220, 220, 220)
BIOFUEL_COLOR = (100, 255, 100)
MARINE_LIFE_COLORS = {
    'shark': (100, 100, 120),
    'turtle': (34, 139, 34),
    'fish': (255, 165, 0)
}
HAZARD_COLORS = {
    'oil': (30, 30, 30),
    'cargo': (139, 69, 19),
    'wave': (135, 206, 235)
}
POWERUP_COLORS = {
    'eco_net': (0, 255, 255),
    'turbo': (255, 0, 255),
    'shield': (0, 255, 127)
}

# Gameplay Parameters
BASE_SCROLL_SPEED = 250
PLAYER_SPEED = 320
MAX_LIVES = 3

# Reference scale – all entity sizes derive from this
BASE_ENTITY_SIZE = 130
PLAYER_SIZE = (int(BASE_ENTITY_SIZE * 0.8), int(BASE_ENTITY_SIZE * 1.2))

# Progression
DIFFICULTY_TIMER = 8.0
SCROLL_SPEED_INC = 30

# Entity probabilities (weights)
SPAWN_RATES = {
    'plastic': 45,
    'marine_life': 25,
    'hazard': 25,
    'powerup': 5
}

# Particle settings
PARTICLE_COLORS_COLLECT = [(100, 255, 180), (80, 220, 255), (200, 255, 200)]
PARTICLE_COLORS_DAMAGE = [(255, 80, 80), (255, 150, 50), (255, 200, 100)]
PARTICLE_COLORS_POWERUP = [(255, 255, 100), (100, 255, 255), (255, 100, 255)]
PARTICLE_COLORS_BUBBLE = [(150, 210, 245, 100), (180, 230, 255, 80), (200, 240, 255, 60)]
