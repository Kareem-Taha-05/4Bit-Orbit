import pygame
from math import sin

class Entity(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.frame_index = 0
        self.animation_speed = 0.1
        self.direction = pygame.math.Vector2()

    def move(self, direction, speed):
        if direction.magnitude() != 0:
            direction.normalize_ip()

        # Store the movement vector for collision detection
        movement_x = speed * direction.x
        movement_y = speed * direction.y

        # Horizontal movement
        self.hitbox.x += movement_x
        self.collision('horizontal', movement_x)
        
        # Vertical movement
        self.hitbox.y += movement_y
        self.collision('vertical', movement_y)

        self.rect.center = self.hitbox.center

    def collision(self, direction, movement_delta=None):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if movement_delta is None:
                        # Fallback to direction-based collision (original behavior)
                        if self.direction.x > 0:  # moving right
                            self.hitbox.right = sprite.hitbox.left
                        elif self.direction.x < 0:  # moving left
                            self.hitbox.left = sprite.hitbox.right
                    else:
                        # Use actual movement delta for more accurate collision
                        if movement_delta > 0:  # moving right
                            self.hitbox.right = sprite.hitbox.left
                        elif movement_delta < 0:  # moving left
                            self.hitbox.left = sprite.hitbox.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if movement_delta is None:
                        # Fallback to direction-based collision (original behavior)
                        if self.direction.y > 0:  # moving down
                            self.hitbox.bottom = sprite.hitbox.top
                        elif self.direction.y < 0:  # moving up
                            self.hitbox.top = sprite.hitbox.bottom
                    else:
                        # Use actual movement delta for more accurate collision
                        if movement_delta > 0:  # moving down
                            self.hitbox.bottom = sprite.hitbox.top
                        elif movement_delta < 0:  # moving up
                            self.hitbox.top = sprite.hitbox.bottom

    def animate(self):
        animation = self.animations[self.state]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

    def wave_value(self):
        value = sin(pygame.time.get_ticks())
        if value >= 0:
            return 255
        else:
            return 0