import pygame
from csv import reader
import os, sys

def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev (Python) and for PyInstaller .exe
    """
    try:
        # PyInstaller creates a temp folder and stores files in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def import_csv_layout(path):
    with open(path) as map:
        layout = reader(map, delimiter=',')
        layout_list = []
        for row in layout:
            layout_list.append(list(row))
        return layout_list
    
def import_image_from_folder(path):
    image_list = []
    for _, __, files in os.walk(path):
        for file in files:
            full_path = path + '/' + file
            image_surf = pygame.image.load(full_path).convert_alpha()
            image_list.append(image_surf)
    return image_list

def load_vertical_animation_sheet(file_path, frame_width, frame_height):
    animation_list = [[],[],[],[]]
    sprite_sheet = pygame.image.load(file_path).convert_alpha()
    rows = sprite_sheet.get_height() // frame_height
    cols = sprite_sheet.get_width() // frame_width
    for col in range(cols):
        for row in range(rows):
            animation_list[col].append(pygame.Surface.subsurface(sprite_sheet, pygame.Rect(col*frame_width, row*frame_height, frame_width, frame_height)))
    return animation_list

def load_horizontal_animation_sheet(file_path, frame_width, frame_height):
    frames = []
    sprite_sheet = pygame.image.load(file_path).convert_alpha()
    cols = sprite_sheet.get_width() // frame_width
    for col in range(cols):
        frames.append(pygame.Surface.subsurface(sprite_sheet, pygame.Rect(col*frame_width, 0, frame_width, frame_height)))
    return frames

def direction_to_vector(direction):
    match direction:
        case 'up': return pygame.math.Vector2(0, -1)
        case 'down': return pygame.math.Vector2(0, 1)
        case 'left': return pygame.math.Vector2(-1, 0)
        case 'right': return pygame.math.Vector2(1, 0)
