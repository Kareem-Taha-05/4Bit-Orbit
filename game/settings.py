#map dimensions
ORIGINAL_TILE_SIZE = 16
SCALE = 4
TILE_SIZE = ORIGINAL_TILE_SIZE*SCALE
SCREEN_WIDTH = 20 * TILE_SIZE
SCREEN_HEIGHT = 12 * TILE_SIZE
FPS = 60
MAP_WIDTH = 200*TILE_SIZE  # Width of the game world in pixels
MAP_HEIGHT = 200*TILE_SIZE  # Height of the game world in pixels


celestial_bodies = {
    '0': 'earth',
    '1': 'jupiter',
    '2': 'mars',
    '3': 'mercury',
    '4': 'neptune',
    '5': 'saturn',
    '6': 'uranus',
    '7': 'venus',
    '8': 'sun'
}