import pygame, state
from settings import *
from entity import Entity
from hitbox import CircleHitbox
from bullet import Bullet
from random import randint
from math import atan2, degrees, cos, sin, radians, sqrt
from utility import resource_path

class Player(Entity):
    def __init__(self, type, pos, groups, obstacle_sprites, bullet_group): 
        super().__init__(groups)
        self.sprite_type = type
        self.obstacle_sprites = obstacle_sprites
        self.bullet_group = bullet_group  

        self.angle = 0
        self.original_image = pygame.image.load(resource_path('graphics/player.png'))  # GRAPHIC NEEDED: Player spaceship sprite
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-20, -40)
        self.hitbox.bottom = self.rect.bottom
        
        # Spaceship movement system
        self.x = float(pos[0])
        self.y = float(pos[1])
        self.speed = 0
        self.max_speed = 5
        self.acceleration = 0.2
        self.friction = 0.92
        self.min_speed_threshold = 0.05  # Speed below this stops the ship
        
        # Store previous position for collision rollback
        self.prev_x = self.x
        self.prev_y = self.y
        
        # Combat system
        self.health = 100
        self.max_health = 100
        self.last_shot = 0
        self.shoot_cooldown = 200  # milliseconds
        self.damage_cooldown = 1000  # milliseconds of invincibility after taking damage
        self.last_damage = 0
        self.invulnerable = False
        self.bullets = 1  # Can be increased with power-ups
        self.shoot_angle = 0
        self.shoot_spread = 5  # degrees of spread for multi-shot
        self.shoot_sound = pygame.mixer.Sound(resource_path('sound/laser.mp3'))  
        self.shoot_sound.set_volume(0.2)

    def input(self):
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
        
        # Rotation - increased sensitivity
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle -= 4.5
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle += 4.5
            
        # Thrust
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.speed = min(self.speed + self.acceleration, self.max_speed)
        else:
            # Only apply friction when not thrusting
            self.speed *= self.friction
        
        # Stop completely if speed is too low to prevent "crawling"
        if self.speed < self.min_speed_threshold:
            self.speed = 0
            
        # Shooting
        if keys[pygame.K_SPACE] or mouse[0]:
            self.shoot()

    # Shooting method with mouse-based aiming
    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot >= self.shoot_cooldown:
            pygame.mixer.Sound.play(self.shoot_sound)
            # Get mouse position in screen space
            mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
            player_pos = pygame.Vector2(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
            mouse_vector = (mouse_pos - player_pos).normalize()

            #calculate the bullet spawn angle
            self.shoot_angle = degrees(atan2(mouse_vector.y, mouse_vector.x))
            
            # Calculate bullet spawn position (spawn from player center)
            rad = radians(self.shoot_angle)
            bullet_x = self.x + cos(rad) * 30  # Spawn bullet 30 pixels ahead
            bullet_y = self.y + sin(rad) * 30
            
            # Create bullet with shooting angle
            for bullet_num in range(self.bullets):  # Can adjust range for multi-shot
                self.shoot_angle += randint(-self.shoot_spread, self.shoot_spread)  # Slight random spread for multi-shot
                bullet = Bullet(bullet_x, bullet_y, self.shoot_angle, [self.bullet_group], owner='player')
            self.last_shot = current_time

    def take_damage(self, damage):
        current_time = pygame.time.get_ticks()
        if not self.invulnerable:
            self.health -= damage
            self.last_damage = current_time
            self.invulnerable = True
            if self.health <= 0:
                self.health = 0
                # Handle player death here if needed

    # Update invulnerability
    def update_combat(self):
        current_time = pygame.time.get_ticks()
        if self.invulnerable and current_time - self.last_damage >= self.damage_cooldown:
            self.invulnerable = False

    def check_collision_with_obstacle(self, obstacle):
        """Check collision between player hitbox and obstacle hitbox (rect or circle)"""
        # Check if obstacle has a circle hitbox
        if isinstance(obstacle.hitbox, CircleHitbox):
            # Circle vs Rectangle collision
            return obstacle.hitbox.colliderect(self.hitbox)
        else:
            # Rectangle vs Rectangle collision (original behavior)
            return obstacle.hitbox.colliderect(self.hitbox)

    def resolve_horizontal_collision(self, obstacle, movement_delta):
        """Resolve horizontal collision with either rect or circle obstacle"""
        if isinstance(obstacle.hitbox, CircleHitbox):
            # Circle collision resolution - push player away from circle center
            circle = obstacle.hitbox
            
            # Calculate direction from circle center to player center
            dx = self.hitbox.centerx - circle.x
            dy = self.hitbox.centery - circle.y
            distance = sqrt(dx * dx + dy * dy)
            
            if distance > 0:  # Avoid division by zero
                # Normalize direction vector
                dx /= distance
                dy /= distance
                
                # Calculate minimum separation distance
                min_distance = circle.radius + max(self.hitbox.width, self.hitbox.height) // 2
                
                # Push player to minimum safe distance, prioritizing horizontal movement
                if movement_delta > 0:  # was moving right
                    self.hitbox.centerx = circle.x + min_distance * abs(dx) * (1 if dx > 0 else -1)
                elif movement_delta < 0:  # was moving left
                    self.hitbox.centerx = circle.x + min_distance * abs(dx) * (1 if dx > 0 else -1)
        else:
            # Rectangle collision resolution (original behavior)
            if movement_delta > 0:  # moving right
                self.hitbox.right = obstacle.hitbox.left
            elif movement_delta < 0:  # moving left
                self.hitbox.left = obstacle.hitbox.right

    def resolve_vertical_collision(self, obstacle, movement_delta):
        """Resolve vertical collision with either rect or circle obstacle"""
        if isinstance(obstacle.hitbox, CircleHitbox):
            # Circle collision resolution - push player away from circle center
            circle = obstacle.hitbox
            
            # Calculate direction from circle center to player center
            dx = self.hitbox.centerx - circle.x
            dy = self.hitbox.centery - circle.y
            distance = sqrt(dx * dx + dy * dy)
            
            if distance > 0:  # Avoid division by zero
                # Normalize direction vector
                dx /= distance
                dy /= distance
                
                # Calculate minimum separation distance
                min_distance = circle.radius + max(self.hitbox.width, self.hitbox.height) // 2
                
                # Push player to minimum safe distance, prioritizing vertical movement
                if movement_delta > 0:  # was moving down
                    self.hitbox.centery = circle.y + min_distance * abs(dy) * (1 if dy > 0 else -1)
                elif movement_delta < 0:  # was moving up
                    self.hitbox.centery = circle.y + min_distance * abs(dy) * (1 if dy > 0 else -1)
        else:
            # Rectangle collision resolution (original behavior)
            if movement_delta > 0:  # moving down
                self.hitbox.bottom = obstacle.hitbox.top
            elif movement_delta < 0:  # moving up
                self.hitbox.top = obstacle.hitbox.bottom

    def collision(self, direction, movement_delta=None):
        """Enhanced collision system supporting both rectangular and circular hitboxes"""
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if self.check_collision_with_obstacle(sprite):
                    if movement_delta is None:
                        # Fallback to direction-based collision (original behavior)
                        if isinstance(sprite.hitbox, CircleHitbox):
                            # Use current direction for circle collision
                            movement_delta = self.direction.x * self.speed if hasattr(self, 'speed') else self.direction.x
                        
                        if self.direction.x > 0:  # moving right
                            self.resolve_horizontal_collision(sprite, 1)
                        elif self.direction.x < 0:  # moving left
                            self.resolve_horizontal_collision(sprite, -1)
                    else:
                        # Use actual movement delta for more accurate collision
                        self.resolve_horizontal_collision(sprite, movement_delta)

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if self.check_collision_with_obstacle(sprite):
                    if movement_delta is None:
                        # Fallback to direction-based collision (original behavior)
                        if isinstance(sprite.hitbox, CircleHitbox):
                            # Use current direction for circle collision
                            movement_delta = self.direction.y * self.speed if hasattr(self, 'speed') else self.direction.y
                        
                        if self.direction.y > 0:  # moving down
                            self.resolve_vertical_collision(sprite, 1)
                        elif self.direction.y < 0:  # moving up
                            self.resolve_vertical_collision(sprite, -1)
                    else:
                        # Use actual movement delta for more accurate collision
                        self.resolve_vertical_collision(sprite, movement_delta)

    def move_and_collide(self):
        # Only move and check collisions if actually moving
        if self.speed > 0:
            # Calculate movement with higher precision
            rad = radians(self.angle)
            movement_x = cos(rad) * self.speed
            movement_y = sin(rad) * self.speed
            
            # Move horizontally and check collision
            self.x += movement_x
            new_hitbox_x = round(self.x)
            self.hitbox.centerx = new_hitbox_x
            self.collision('horizontal', movement_x)
            # If collision occurred, update our float position to match
            if self.hitbox.centerx != new_hitbox_x:
                self.x = self.hitbox.centerx
            
            # Move vertically and check collision
            self.y += movement_y
            new_hitbox_y = round(self.y)
            self.hitbox.centery = new_hitbox_y
            self.collision('vertical', movement_y)

            # If collision occurred, update our float position to match
            if self.hitbox.centery != new_hitbox_y:
                self.y = self.hitbox.centery
            
            # Update direction vector for compatibility with other systems
            self.direction.x = cos(rad)
            self.direction.y = sin(rad)
        else:
            # Not moving, just update hitbox position without collision checks
            self.hitbox.centerx = round(self.x)
            self.hitbox.centery = round(self.y)
            self.direction.x = 0
            self.direction.y = 0

    def rotate_image(self):
        self.image = pygame.transform.rotozoom(self.original_image, -self.angle - 90, 1)
        self.rect = self.image.get_rect()
        self.rect.center = (round(self.x), round(self.y))

    def update(self):
        self.input()
        self.move_and_collide()
        self.rotate_image()
        self.update_combat() 
        
        # Ensure rect matches final position
        self.rect.center = self.hitbox.center
