import pygame
from pathlib import Path

# --- SCREEN ---
ANCHO, ALTO = 1080, 600
FPS = 60

# --- COLORS ---
BG_COLOR = (125, 125, 125)
WALL_COLOR = (0, 0, 0)
POINT_COLOR = (50, 140, 240)
TEXT_COLOR = (255, 255, 255)

# --- PATHS ---
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
IMG_DIR = ASSETS_DIR / "images"
SOUND_DIR = ASSETS_DIR / "sounds"
LEVEL_DIR = ASSETS_DIR / "levels"

# --- ENTITY SETTINGS ---
PACMAN_SPEED = 300 # Pixels per second
GHOST_SPEED = 120 # Pixels per second
GHOST_START_POS = (540, 150)
GHOST_RELEASE_TIMES = [1.0, 3.0, 5.0] # Delay in seconds from game start

LEVELS = ["Zona 1.txt", "Zona 2.txt", "Zona 3.txt"]

def load_image(name, colorkey=None):
    """Utility to load an image."""
    path = IMG_DIR / name
    try:
        image = pygame.image.load(str(path)).convert_alpha()
        return image
    except FileNotFoundError:
        print(f"Cannot load image: {path}")
        # Return a fallback surface
        surf = pygame.Surface((30, 30))
        surf.fill((255, 0, 0))
        return surf

def load_sound(name):
    """Utility to load a sound."""
    path = SOUND_DIR / name
    try:
        return pygame.mixer.Sound(str(path))
    except (FileNotFoundError, pygame.error):
        print(f"Cannot load sound: {path}")
        return None
