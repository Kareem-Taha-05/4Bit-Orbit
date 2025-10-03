import pygame
from utility import load_horizontal_animation_sheet, resource_path
from hitbox import CircleHitbox

class Planet(pygame.sprite.Sprite):
    def __init__(self, name, x, y, groups):
        super().__init__(groups)
        self.name = name
        self.sprite_type = 'planet'
        self.x = x
        self.y = y
        
        self.import_assets()
        self.image = self.animation[0]
        self.rect = self.image.get_rect(center = (x, y))
        if self.name == 'sun':
            self.hitbox = CircleHitbox(x, y, self.image.get_height()//4)
        else:
            self.hitbox = CircleHitbox(x, y, self.image.get_height()//2)
        self.frame_index = 0
        self.animation_speed = 0.005

    def import_assets(self):
        reference = pygame.image.load(resource_path(f'graphics/planets/{self.name}/reference.png'))
        self.animation = load_horizontal_animation_sheet(resource_path(f'graphics/planets/{self.name}/sheet.png'), reference.get_width(), reference.get_height())

    def animate(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.animation):
            self.frame_index = 0
        self.image = self.animation[int(self.frame_index)]

    def update(self):
        self.animate()