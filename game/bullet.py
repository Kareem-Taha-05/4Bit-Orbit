import pygame
from math import radians, cos, sin, sqrt
from utility import resource_path

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, groups, owner='player'):
        super().__init__(groups)
        self.sprite_type = 'bullet'
        self.owner = owner  # 'player' or 'enemy'
        
        # Load bullet image
        try:
            if self.owner == 'player':
                self.original_image = pygame.image.load(resource_path('graphics/bullet.png')).convert_alpha() 
            else :
                self.original_image = pygame.image.load(resource_path('graphics/enemy_bullet.png')).convert_alpha()
            # Scale if needed (adjust size as needed)
            self.original_image = pygame.transform.scale(self.original_image, (16, 16))
        except:
            # Fallback to simple surface if image not found
            self.original_image = pygame.Surface((16, 16))
            if owner == 'player':
                self.original_image.fill('yellow')
            else:
                self.original_image.fill('red')
        
        self.angle = angle
        self.x = float(x)
        self.y = float(y)
        if self.owner == 'player':
            self.speed = 12
            self.damage = 10
            self.max_distance = 600  # Bullets disappear after traveling this distance
        elif self.owner == 'enemy':
            self.speed = 3
            self.damage = 15
            self.max_distance = 400
        else:
            self.speed = 5
            self.damage = 5
            self.max_distance = 800  # Bullets disappear after traveling this distance
        self.start_x = x
        self.start_y = y
        
        # Calculate movement direction
        rad = radians(angle)
        self.velocity_x = cos(rad) * self.speed
        self.velocity_y = sin(rad) * self.speed
        
        # Rotate bullet image to match shooting angle
        self.image = pygame.transform.rotate(self.original_image, -angle)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        # Move bullet
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.rect.centerx = round(self.x)
        self.rect.centery = round(self.y)
        
        # Remove bullet if it travels too far
        distance_traveled = sqrt((self.x - self.start_x)**2 + (self.y - self.start_y)**2)
        if distance_traveled > self.max_distance:
            self.kill()
