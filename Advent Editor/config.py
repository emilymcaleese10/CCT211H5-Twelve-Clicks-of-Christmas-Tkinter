import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SHAPES_DIR = os.path.join(BASE_DIR, "shapes")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DB_FILE = os.path.join(BASE_DIR, "advent.db")


WINDOW_WIDTH = 760
WINDOW_HEIGHT = 360
PEACH = "#dba582"

# Advent dates: 12-day calendar, days 13–24
DOOR_DATES = [13 + i for i in range(12)]

# Ensure assets directory exists
os.makedirs(ASSETS_DIR, exist_ok=True)
