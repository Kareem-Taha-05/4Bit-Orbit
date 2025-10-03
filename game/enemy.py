import pygame
from math import sqrt, degrees, atan2, radians, sin, cos
from hitbox import CircleHitbox
from bullet import Bullet
from settings import *
from utility import resource_path

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, groups, obstacle_sprites):
        super().__init__(groups)
        self.sprite_type = 'enemy'
        self.obstacle_sprites = obstacle_sprites
        
        # Create a simple enemy graphic (you can replace with an image)
        self.original_image = pygame.image.load(resource_path('graphics/enemy.png'))  # GRAPHIC NEEDED: Replace with enemy sprite
        # self.original_image.fill('red')  # Simple red square for now
        
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.hitbox = self.rect.inflate(-8, -8)
        
        # Position tracking
        self.x = float(x)
        self.y = float(y)
        
        # Movement properties
        self.speed = 1.5
        self.angle = 0
        
        # Combat properties
        self.health = 50
        self.max_health = 50
        self.damage = 20
        self.attack_range = 40
        self.last_attack = 0
        self.attack_cooldown = 1500  # milliseconds
        
        self.shoot_range = 300  # Range at which enemy starts shooting
        self.last_shot = 0
        self.shoot_cooldown = 1000  # milliseconds between shots
        self.bullet_group = None  # Will be set by level
        
        # AI properties
        self.detection_range = 500 # Range to detect player
        self.target = None
        
        # Death flag for chunk system cleanup
        self.dead = False

    def find_target(self, player):
        """Check if player is within detection range"""
        distance = sqrt((player.x - self.x)**2 + (player.y - self.y)**2)
        if distance <= self.detection_range:
            self.target = player
        else:
            self.target = None

    def move_towards_target(self):
        """Move towards the target player"""
        if self.target:
            # Calculate direction to target
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            distance = sqrt(dx**2 + dy**2)
            
            if distance > self.shoot_range:  # Only move if not in shooting range
                if distance > 0:  # Avoid division by zero
                    # Normalize direction and apply speed
                    dx = (dx / distance) * self.speed
                    dy = (dy / distance) * self.speed
                    
                    # Move and check collisions
                    self.x += dx
                    self.hitbox.centerx = round(self.x)
                    self.check_collisions('horizontal')
                    
                    self.y += dy
                    self.hitbox.centery = round(self.y)
                    self.check_collisions('vertical')
                    
                    # Update angle for rotation
                    self.angle = degrees(atan2(dy, dx))
            else:
                self.angle = degrees(atan2(dy, dx))

    def check_collisions(self, direction):
        """Simple collision detection with obstacles"""
        for sprite in self.obstacle_sprites:
            if hasattr(sprite, 'hitbox'):
                if isinstance(sprite.hitbox, CircleHitbox):
                    if sprite.hitbox.colliderect(self.hitbox):
                        if direction == 'horizontal':
                            if self.x > sprite.hitbox.x:
                                self.hitbox.left = sprite.hitbox.x + sprite.hitbox.radius
                            else:
                                self.hitbox.right = sprite.hitbox.x - sprite.hitbox.radius
                            self.x = self.hitbox.centerx
                        else:  # vertical
                            if self.y > sprite.hitbox.y:
                                self.hitbox.top = sprite.hitbox.y + sprite.hitbox.radius
                            else:
                                self.hitbox.bottom = sprite.hitbox.y - sprite.hitbox.radius
                            self.y = self.hitbox.centery
                elif sprite.hitbox.colliderect(self.hitbox):
                    if direction == 'horizontal':
                        if self.x > sprite.hitbox.centerx:
                            self.hitbox.left = sprite.hitbox.right
                        else:
                            self.hitbox.right = sprite.hitbox.left
                        self.x = self.hitbox.centerx
                    else:  # vertical
                        if self.y > sprite.hitbox.centery:
                            self.hitbox.top = sprite.hitbox.bottom
                        else:
                            self.hitbox.bottom = sprite.hitbox.top
                        self.y = self.hitbox.centery

    def shoot_at_target(self):
        """Shoot bullets at the target if in range"""
        if self.target and self.bullet_group is not None:
            distance = sqrt((self.target.x - self.x)**2 + (self.target.y - self.y)**2)
            current_time = pygame.time.get_ticks()  
            
            if (distance <= self.shoot_range and 
                current_time - self.last_shot >= self.shoot_cooldown):
                # Calculate angle to player
                dx = self.target.x - self.x
                dy = self.target.y - self.y
                shoot_angle = degrees(atan2(dy, dx))
                
                # Calculate bullet spawn position (spawn from enemy center)
                rad = radians(shoot_angle)
                bullet_x = self.x + cos(rad) * 20  # Spawn bullet 20 pixels ahead
                bullet_y = self.y + sin(rad) * 20
                
                # Create enemy bullet with 'enemy' owner
                bullet = Bullet(bullet_x, bullet_y, shoot_angle, [self.bullet_group], owner='enemy')
                self.last_shot = current_time

    def attack_target(self):
        """Attack the target if in melee range (kept for close combat)"""
        if self.target:
            distance = sqrt((self.target.x - self.x)**2 + (self.target.y - self.y)**2)
            current_time = pygame.time.get_ticks()
            
            if (distance <= self.attack_range and 
                current_time - self.last_attack >= self.attack_cooldown):
                self.target.take_damage(self.damage)
                self.last_attack = current_time

    def take_damage(self, damage):
        """Take damage and handle death"""
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            # Mark for removal from chunk system
            self.dead = True
            self.die()

    def rotate_image(self):
        """Rotate sprite to face movement direction"""
        self.image = pygame.transform.rotate(self.original_image, -self.angle - 90)
        self.rect = self.image.get_rect(center=self.hitbox.center)
    
    def die(self):
        # Notify story manager
        if hasattr(self, 'level') and hasattr(self.level, 'story_manager'):
            self.level.story_manager.on_enemy_killed()
        self.kill()

    def enemy_update(self, player):
        """Main enemy update method called from level"""
        self.find_target(player)
        self.move_towards_target()
        self.shoot_at_target()
        self.attack_target()  # Keep melee attack for close range
        self.rotate_image()
        self.rect.center = self.hitbox.center
        
class EnemySpawner:
    def __init__(self, level):
        self.level = level
        self.spawn_timer = 0
        self.spawn_interval = 5000  # Spawn enemy every 5 seconds
        self.max_enemies = 10  # Maximum enemies on screen
        self.spawn_distance = 600  # Spawn enemies this far from player

    def update(self, player):
        """Update spawner and spawn enemies if needed"""
        current_time = pygame.time.get_ticks()
        
        # Count current enemies
        current_enemies = len([sprite for sprite in self.level.visible_sprites 
                             if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'enemy'])
        
        # Spawn new enemy if conditions are met
        if (current_time - self.spawn_timer >= self.spawn_interval and 
            current_enemies < self.max_enemies):
            self.spawn_enemy(player)
            self.spawn_timer = current_time

    def spawn_enemy(self, player):
        """Spawn an enemy at a random location around the player"""
        import random
        
        # Generate random angle
        angle = random.uniform(0, 360)
        rad = radians(angle)
        
        # Calculate spawn position
        spawn_x = player.x + cos(rad) * self.spawn_distance
        spawn_y = player.y + sin(rad) * self.spawn_distance
        
        # Create enemy and add to level
        if 0 <= spawn_x <= MAP_WIDTH and 0 <= spawn_y <= MAP_HEIGHT:
            enemy = Enemy(spawn_x, spawn_y, [], self.level.obstacle_sprites)
            enemy.level = self.level
            enemy.bullet_group = self.level.bullet_group
            self.level.add_to_chunk(enemy, spawn_x, spawn_y)
