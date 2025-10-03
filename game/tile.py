import pygame
from settings import *

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, sprite_type, surface = pygame.Surface((TILE_SIZE, TILE_SIZE))):
        super().__init__(groups)
        self.sprite_type = sprite_type
        self.image = surface.convert_alpha()
        if self.sprite_type == 'object':
            height = self.image.get_height() // TILE_SIZE
            self.rect = self.image.get_rect(topleft = (pos[0], pos[1] - (height-1)*TILE_SIZE)) # raise the rect by the height - 1 Tile
            self.hitbox = self.rect.inflate(-10, -((height)*TILE_SIZE*2//3)) # shrink hitbox height by 2/3 of the height
            self.hitbox.bottom = self.rect.bottom - 20 # raise the hitbox from the bottom of the image by a little 
        elif self.sprite_type == 'grass':
            self.rect = self.image.get_rect(topleft = pos)
            self.hitbox = self.rect.inflate(-10, -10)
        else:
            self.rect = self.image.get_rect(topleft = pos)
            self.hitbox = self.rect.inflate(0, 0)
        if self.sprite_type == 'invisible':
            self.image.set_alpha(0)