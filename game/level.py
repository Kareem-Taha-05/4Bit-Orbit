import pygame
import state
from player import Player  
from enemy import Enemy, EnemySpawner
from tile import Tile
from settings import *
from utility import import_csv_layout, import_image_from_folder, resource_path
from random import choice
from event import Event
from planet import Planet
from hitbox import CircleHitbox
from math import sin, floor, sqrt, atan2, cos
from dialog import StoryManager
from event_manager import EventManager
from debug import debug
from quiz import Quiz

class LevelManager:
    def __init__(self):
        self.current_level = None
        self.current_level_state = None
        self.quiz = None

    def create_level(self, level_state):
        level_name = 'map_' + str(level_state.value)
        return Level(level_name)
    
    def handle_events(self, event):
        if state.PLAY_STATE == state.PlayState.QUIZ:
            if self.quiz:
                self.quiz.handle_events(event)
        elif self.current_level:
            self.current_level.handle_events(event)

    def update(self):
        if self.current_level_state != state.LEVEL_STATE:
            self.current_level = self.create_level(state.LEVEL_STATE)
            self.current_level_state = state.LEVEL_STATE

        if state.PLAY_STATE == state.PlayState.QUIZ:
            if not self.quiz:
                self.quiz = Quiz()
            self.quiz.draw()
        else:
            if self.current_level:
                self.current_level.run()

class Level:
    def __init__(self, level_name):
        # display surface
        self.display_surface = pygame.display.get_surface()
        self.level_name = level_name
        self.game_paused = False

        # sprite groups
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group() 
        self.bullet_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()

        # events
        self.events = []
        self.event_timer = pygame.USEREVENT + 1
        self.can_activate_event = False
        
        # NEW: Event management system
        self.event_manager = None  # Will be initialized after player is created
        
        # NEW: Story management system
        self.story_manager = None  # Will be initialized after player is created

        # chunk system
        self.chunk_size = 1000
        self.chunks = {}
        self.obstacle_chunks = {}

        # Enemy spawning system
        self.enemy_spawner = None

        # Pre-place static objects (planets, stations, etc.)
        static_objects = [
            # Add later
        ]

        for obj in static_objects:
            self.add_object(obj, (obj.x, obj.y), is_obstacle=True)

        # setup map
        self.create_map()
        
        # NEW: Initialize story manager after map is created
        self.story_manager = StoryManager(self)
        
        # NEW: Initialize event manager and create events
        self.event_manager = EventManager(self)
        
        # CREATE YOUR EVENTS HERE - Choose which chapters to load:
        self.event_manager.setup_chapter_1_events()
        # self.event_manager.setup_chapter_2_events()  # Uncomment for chapter 2
        # self.event_manager.setup_tutorial_events()   # Uncomment for tutorial
        # self.event_manager.setup_custom_events()     # Add custom events

    def add_to_chunk(self, sprite, x, y, is_obstacle=False):
        """Add a sprite to the correct chunk based on world coords."""
        cx = x // self.chunk_size
        cy = y // self.chunk_size
        
        if (cx, cy) not in self.chunks:
            self.chunks[(cx, cy)] = []
        self.chunks[(cx, cy)].append(sprite)
        
        if is_obstacle:
            if (cx, cy) not in self.obstacle_chunks:
                self.obstacle_chunks[(cx, cy)] = []
            self.obstacle_chunks[(cx, cy)].append(sprite)
    
    def remove_from_chunks(self, sprite):
        """Remove a sprite from all chunks (used for enemy death)"""
        for chunk_list in self.chunks.values():
            if sprite in chunk_list:
                chunk_list.remove(sprite)
        
        for chunk_list in self.obstacle_chunks.values():
            if sprite in chunk_list:
                chunk_list.remove(sprite)
    
    def clean_dead_enemies(self):
        """Remove dead enemies from chunk system"""
        for chunk_key in list(self.chunks.keys()):
            # Remove enemies that have been killed (no longer in any groups)
            self.chunks[chunk_key] = [s for s in self.chunks[chunk_key] 
                                    if not (hasattr(s, 'sprite_type') and 
                                            s.sprite_type == 'enemy' and 
                                            hasattr(s, 'dead') and s.dead)]
        
        for chunk_key in list(self.obstacle_chunks.keys()):
            self.obstacle_chunks[chunk_key] = [s for s in self.obstacle_chunks[chunk_key] 
                                            if not (hasattr(s, 'sprite_type') and 
                                                    s.sprite_type == 'enemy' and 
                                                    hasattr(s, 'dead') and s.dead)]


    def get_active_chunks(self):
        """Return all sprites from chunks around the player."""
        player_cx = int(self.player.x) // self.chunk_size
        player_cy = int(self.player.y) // self.chunk_size

        active = []
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                key = (player_cx + dx, player_cy + dy)
                if key in self.chunks:
                    active.extend(self.chunks[key])  # Just add everything
        return active

    def get_active_obstacles(self):
        """Return all obstacle sprites from chunks around the player."""
        player_cx = int(self.player.x) // self.chunk_size
        player_cy = int(self.player.y) // self.chunk_size

        active_obstacles = []
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                key = (player_cx + dx, player_cy + dy)
                if key in self.obstacle_chunks:
                    active_obstacles.extend(self.obstacle_chunks[key])
        return active_obstacles
        
    def _get_chunk_coords(self, pos):
        x, y = pos
        return (floor(x / self.chunk_size), floor(y / self.chunk_size))
    
    def add_object(self, obj, pos, is_obstacle = False):
        cx, cy = self._get_chunk_coords(pos)
        if (cx, cy) not in self.chunks:
            self.chunks[(cx, cy)] = []
        self.chunks[(cx, cy)].append(obj)

        if is_obstacle:
            if (cx, cy) not in self.obstacle_chunks:
                self.obstacle_chunks[(cx, cy)] = []
            self.obstacle_chunks[(cx, cy)].append(obj)

    def create_map(self):
        layouts = {
            'floorblocks': import_csv_layout(resource_path(f'graphics/maps/{self.level_name}/map_data/{self.level_name}_floorblocks.csv')),
            # 'grass': import_csv_layout(resource_path(f'graphics/maps/{self.level_name}/map_data/{self.level_name}_grass.csv')),
            # 'objects': import_csv_layout(resource_path(f'graphics/maps/{self.level_name}/map_data/{self.level_name}_objects.csv')),
            'entities': import_csv_layout(resource_path(f'graphics/maps/{self.level_name}/map_data/{self.level_name}_entities.csv')),
            'events': import_csv_layout(resource_path(f'graphics/maps/{self.level_name}/map_data/{self.level_name}_entities.csv')),
            'planets': import_csv_layout(resource_path(f'graphics/maps/{self.level_name}/map_data/{self.level_name}_planets.csv')),

        }
        graphics = {
            # 'grass': import_image_from_folder(resource_path('graphics/maps/' + self.level_name + '/grass')),
            # 'objects': import_image_from_folder(resource_path('graphics/maps/' + self.level_name + '/objects')),
        }

        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, val in enumerate(row):
                    if val != '-1':
                        x = col_index * TILE_SIZE
                        y = row_index * TILE_SIZE

                        if style == 'floorblocks':
                            tile = Tile((x, y), [], 'invisible')
                            self.add_to_chunk(tile, x, y, is_obstacle=True)

                        if style == 'grass':
                            grass_surf = choice(graphics['grass'])
                            tile = Tile((x, y), [], 'grass', grass_surf)
                            self.add_to_chunk(tile, x, y, is_obstacle=True)

                        if style == 'objects':
                            object_surf = graphics['objects'][int(val)]
                            tile = Tile((x, y), [], 'object', object_surf)
                            self.add_to_chunk(tile, x, y, is_obstacle=True)

                        if style == 'entities':
                            if val == '394':
                                self.player = Player(
                                    'player',  # Changed from 'type' to 'player'
                                    (124*TILE_SIZE, 80*TILE_SIZE),
                                    [],
                                    self.obstacle_sprites,
                                    self.bullet_group
                                )
                                self.add_to_chunk(self.player, x, y)
                                self.enemy_spawner = EnemySpawner(self)
                        if style == 'planets':
                            planet = Planet(celestial_bodies[str(val)], x, y, [])
                            self.add_to_chunk(planet, x, y, is_obstacle=True)
                        # # OPTIONAL: You can still create events from CSV if you want
                        # if style == 'events':
                        #     event = Event(x, y, [], 'CSV Event', 'From map', 
                        #                  (100, 200, 255), event_id='csv_event')
                        #     self.add_to_chunk(event, x, y)
                        #     self.events.append(event)

    def check_bullet_collisions(self):
        """Check collisions between bullets and their targets"""
        for bullet in self.bullet_group:
            # Player bullets hit enemies
            if bullet.owner == 'player':
                for sprite in self.visible_sprites:
                    if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'enemy':
                        if bullet.rect.colliderect(sprite.rect):
                            sprite.take_damage(bullet.damage)
                            bullet.kill()
                            break
            
            # Enemy bullets hit player
            elif bullet.owner == 'enemy':
                if bullet.rect.colliderect(self.player.rect):
                    self.player.take_damage(bullet.damage)
                    bullet.kill()
                    continue
            
            # All bullets collide with obstacles
            for obstacle in self.obstacle_sprites:
                if hasattr(obstacle, 'hitbox'):
                    if isinstance(obstacle.hitbox, CircleHitbox):
                        if obstacle.hitbox.collidepoint(bullet.rect.center):
                            bullet.kill()
                            break
                    elif obstacle.hitbox.colliderect(bullet.rect):
                        bullet.kill()
                        break

    def handle_events(self, event):
        self.visible_sprites.handle_events(event)
        
        # NEW: Pass events to story manager
        if hasattr(self, 'story_manager') and self.story_manager:
            self.story_manager.handle_events(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                print('event handled')
            
            # NEW: E key to interact with manual events (passed to EventManager)
            if event.key == pygame.K_e:
                if hasattr(self, 'event_manager') and self.event_manager:
                    self.event_manager.check_manual_event_interaction(self.player)
        
        if event.type == self.event_timer:
            self.can_activate_event = True

    def update_events(self):
        self.active_events = [event for event in self.events if event.is_active]
        for event in self.active_events:
            event.update()
        if self.can_activate_event and self.events:
            event = choice(self.events)
            if not event.is_active:
                event.activate()
                # print('activated event')
            self.can_activate_event = False
    
    def restart(self):
        def switch_restart():
            state.GAME_STATE = state.GameState.RESTART
            print('switched game state to restart')
        self.visible_sprites.custom_draw(self.player, self.story_manager)
        
        if self.story_manager:
                self.story_manager.update()
                self.story_manager.draw()

        if not self.story_manager.dialog_box.active:
            self.story_manager.dialog_box.show_dialog(
                speaker='Aether',
                text_lines=[
                    'Ah… so even the brightest star may falter.',
                    'Do not despair, child of starlight. Each fall is but a step upon the path to wisdom.',
                    'Rise, and try once more.'
                ],
                voice_lines=[resource_path('sound/aether_game_over_1.mp3'),resource_path('sound/aether_game_over_2.mp3'),
                             resource_path('sound/aether_game_over_3.mp3')],
                icons=[resource_path('graphics/icons/aether_closed.png')]*3,
                on_complete= lambda : switch_restart()
            )

    def run(self):
        
        if self.player.health <= 0:
            self.restart()
            return
        
        self.clean_dead_enemies()

        active_sprites = self.get_active_chunks()
        active_obstacles = self.get_active_obstacles()
        
        self.visible_sprites.empty()
        self.obstacle_sprites.empty()
        
        self.visible_sprites.add(self.player)
        
        for sprite in active_sprites:
            if sprite != self.player:
                self.visible_sprites.add(sprite)
        
        self.visible_sprites.add(self.bullet_group.sprites())
        
        self.obstacle_sprites.add(active_obstacles)
        self.visible_sprites.events = self.events
        self.visible_sprites.custom_draw(self.player, self.story_manager)

        if self.story_manager:
                self.story_manager.update()
                self.story_manager.draw()

        if state.PLAY_STATE != state.PlayState.DIALOG:
            if self.enemy_spawner:
                self.enemy_spawner.update(self.player)
        
            self.check_bullet_collisions()
            
            self.visible_sprites.update()
            self.bullet_group.update()
            self.update_events()
        
            if self.event_manager:
                self.event_manager.check_event_collisions(self.player)

            self.visible_sprites.enemy_update(self.player)
        
        # debug(f"Speed: {self.player.speed:.2f}, Pos: ({int(self.player.x)}, {int(self.player.y)}), Health: {self.player.health}")

class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        
        # center camera
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        # box camera
        self.camera_borders = {'left' : 200, 'right' : 200, 'top' : 100, 'bottom' : 100}
        left = self.camera_borders['left']
        top = self.camera_borders['top']
        width = self.display_surface.get_size()[0] - self.camera_borders['right'] - left
        height = self.display_surface.get_size()[1] - self.camera_borders['bottom'] - top
        self.camera_rect = pygame.Rect(left, top, width, height)

        # camera speed
        self.keyboard_speed = 5
        self.mouse_speed = 0.4

        #zoom
        self.zoom_scale = 1
        self.internal_surf_area = (2500, 2500)
        self.internal_surf = pygame.Surface(self.internal_surf_area, pygame.SRCALPHA)
        self.internal_rect = self.internal_surf.get_rect(center = (self.half_width, self.half_height))
        self.internal_surf_area_vect = pygame.math.Vector2(self.internal_surf_area)
        self.internal_offset = pygame.math.Vector2()
        self.internal_offset.x = self.internal_surf_area[0]//2 - self.half_width
        self.internal_offset.y = self.internal_surf_area[1]//2 - self.half_height

        self.floor_surf = pygame.image.load(resource_path('graphics/maps/map_0/map_data/map_0_floor.png')).convert()
        self.floor_rect = self.floor_surf.get_rect(topleft = (0,0))

        #ui
        self.health_bar_bg = pygame.image.load(resource_path('graphics/ui/health_bar_bg.png')).convert_alpha()
        self.health_bar_bg_rect = self.health_bar_bg.get_rect(topleft = (10,10))
        self.health_bar = pygame.image.load(resource_path('graphics/ui/health_bar.png')).convert_alpha()
    
    def center_camera(self, target):
        # Use the player's actual position (x, y) instead of rect
        self.offset.x = target.x - self.half_width
        self.offset.y = target.y - self.half_height

    def handle_events(self, event):
        if event.type == pygame.MOUSEWHEEL:
            if event.y < 0:
                if self.zoom_scale > 0.52:
                    self.zoom_scale += event.y * 0.03
            if event.y >= 1:
                if self.zoom_scale < 1.25:
                    self.zoom_scale += event.y * 0.03


    def draw_event_pointers(self, player, events):
        """Draw arrows at screen edges pointing to off-screen cosmic events"""
        # Only show pointers for the 5 main cosmic events
        cosmic_event_ids = ['solar_flares', 'geomagnetic_storms', 'ionosphere_disturbances', 
                           'solar_energetic_particles', 'cosmic_rays']
        
        screen_width = self.display_surface.get_width()
        screen_height = self.display_surface.get_height()
        arrow_size = 20
        margin = 30  # Distance from screen edge
        
        for event in events:
            # Skip if not a cosmic event or already captured
            if not event.event_id in cosmic_event_ids or event.captured:
                continue
            
            # Calculate event position relative to screen
            event_screen_x = event.x - self.offset.x
            event_screen_y = event.y - self.offset.y
            
            # Check if event is off-screen
            is_offscreen = (event_screen_x < 0 or event_screen_x > screen_width or
                          event_screen_y < 0 or event_screen_y > screen_height)
            
            if is_offscreen:
                # Calculate direction from player to event
                dx = event.x - player.x
                dy = event.y - player.y
                angle = atan2(dy, dx)
                
                # Calculate arrow position at screen edge
                # Start from center of screen
                center_x = screen_width / 2
                center_y = screen_height / 2
                
                # Calculate intersection with screen edges
                # Extend ray from center in direction of event
                ray_length = max(screen_width, screen_height)
                ray_x = center_x + cos(angle) * ray_length
                ray_y = center_y + sin(angle) * ray_length
                
                # Clamp to screen edges with margin
                arrow_x = max(margin, min(screen_width - margin, ray_x))
                arrow_y = max(margin, min(screen_height - margin, ray_y))
                
                # Clamp to actual screen boundaries
                if ray_x < 0:
                    arrow_x = margin
                    arrow_y = center_y + (margin - center_x) * (ray_y - center_y) / (ray_x - center_x)
                elif ray_x > screen_width:
                    arrow_x = screen_width - margin
                    arrow_y = center_y + (screen_width - margin - center_x) * (ray_y - center_y) / (ray_x - center_x)
                
                if ray_y < 0:
                    arrow_y = margin
                    arrow_x = center_x + (margin - center_y) * (ray_x - center_x) / (ray_y - center_y)
                elif ray_y > screen_height:
                    arrow_y = screen_height - margin
                    arrow_x = center_x + (screen_height - margin - center_y) * (ray_x - center_x) / (ray_y - center_y)
                
                # Draw arrow pointing toward event
                self.draw_arrow(arrow_x, arrow_y, angle, arrow_size, event.color)
                
                # Draw event name near arrow
                font = pygame.font.Font(None, 18)
                name_text = font.render(event.name, True, 'white')
                text_rect = name_text.get_rect(center=(arrow_x, arrow_y - 25))
                
                # Draw text background for readability
                bg_rect = text_rect.inflate(10, 5)
                bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
                bg_surface.fill((0, 0, 0, 180))
                self.display_surface.blit(bg_surface, bg_rect)
                self.display_surface.blit(name_text, text_rect)
    
    def draw_arrow(self, x, y, angle, size, color):
        """Draw an arrow at position (x, y) pointing in direction angle"""
        # Arrow tip
        tip_x = x + cos(angle) * size
        tip_y = y + sin(angle) * size
        
        # Arrow base (two points forming the tail)
        base_angle1 = angle + 2.5  # ~143 degrees offset
        base_angle2 = angle - 2.5  # ~143 degrees offset
        
        base1_x = x + cos(base_angle1) * (size * 0.6)
        base1_y = y + sin(base_angle1) * (size * 0.6)
        
        base2_x = x + cos(base_angle2) * (size * 0.6)
        base2_y = y + sin(base_angle2) * (size * 0.6)
        
        # Draw arrow triangle
        points = [(tip_x, tip_y), (base1_x, base1_y), (base2_x, base2_y)]
        pygame.draw.polygon(self.display_surface, color, points)
        pygame.draw.polygon(self.display_surface, 'white', points, 2)  # White outline

    def custom_draw(self, player, story_manager):
        self.center_camera(player)

        offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surf, offset_pos)

        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.bottom):
            if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'player' and sprite.invulnerable:
                if int(pygame.time.get_ticks() / 100) % 2:
                    offset_pos = sprite.rect.topleft - self.offset
                    self.display_surface.blit(sprite.image, offset_pos)
            elif hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'event':
                if sprite.is_active or not sprite.captured:
                    sprite.draw(self.display_surface, self.offset)
            else:
                offset_pos = sprite.rect.topleft - self.offset
                self.display_surface.blit(sprite.image, offset_pos)
        
        # self.draw_health_bar(player)
        self.show_meter(player.health, player.max_health, self.health_bar_bg, self.health_bar_bg_rect, self.health_bar, 4, 4)
        self.draw_event_count(story_manager)
        
        if hasattr(self, 'events'):
            self.draw_event_pointers(player, self.events)
    
    def draw_health_bar(self, player):
        bar_width = 200
        bar_height = 20
        bar_x = 10
        bar_y = 50
        
        # Background bar (red)
        pygame.draw.rect(self.display_surface, 'red', 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # Health bar (green)
        health_percentage = player.health / player.max_health
        health_width = int(bar_width * health_percentage)
        pygame.draw.rect(self.display_surface, 'green', 
                        (bar_x, bar_y, health_width, bar_height))
        
        # Border
        pygame.draw.rect(self.display_surface, 'white', 
                        (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Health text
        font = pygame.font.Font(None, 24)
        health_text = font.render(f"Health: {player.health}/{player.max_health}", True, 'white')
        self.display_surface.blit(health_text, (bar_x, bar_y - 25))
    
    def show_meter(self, current, max, bg_surf, bg_rect, bar_surf, x_offset, y_offset):
        # clamp current between 0 and max
        if current < 0:
            current = 0
        if current > max:
            current = max

        # calculate bar width based on current
        if max == 0:
            bar_width = bar_surf.get_width()
        else:
            bar_width = int(bar_surf.get_width() * (current / max))

        # get the bar surf based on the bar width
        current_bar_surf = pygame.Surface.subsurface(
            bar_surf,
            pygame.Rect(0, 0, bar_width, bar_surf.get_height())
        )

        # position based on top-left instead of bottom-left
        offset = pygame.math.Vector2(x_offset, y_offset)
        current_bar_rect = current_bar_surf.get_rect(topleft=bg_rect.topleft + offset)

        # draw
        self.display_surface.blit(bg_surf, bg_rect)
        self.display_surface.blit(current_bar_surf, current_bar_rect)

    def draw_event_count(self, story_manager):
        font = pygame.font.Font(None, 24)
        event_text = font.render(f"Events Completed: {story_manager.get_flag('events_seen', 0)}/5", True, 'white')
        text_rect = event_text.get_rect(topright=(self.display_surface.get_width() - 10, 10))
        self.display_surface.blit(event_text, text_rect)

    def enemy_update(self, player):
        enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'enemy']
        for enemy in enemy_sprites:
            enemy.enemy_update(player)
