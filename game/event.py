# ============================================================================
# event.py - COMPLETE EVENT CLASS WITH COLLISION AND TRIGGERING
# ============================================================================
import pygame
from math import sin, sqrt
from utility import load_horizontal_animation_sheet, resource_path

class Event(pygame.sprite.Sprite):
    def __init__(self, x, y, groups, name, info, color, event_id=None, visible=True, auto=False, animated=False):
        super().__init__(groups)
        self.x = x
        self.y = y
        self.sprite_type = 'event'
        self.name = name
        self.info = info
        self.color = color
        self.event_id = event_id
        self.captured = False
        self.triggered = False
        self.trigger_once = True
        self.radius = 30
        self.trigger_radius = 50
        self.pulse = 0
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)
        self.is_active = False
        self.visible = visible  # If false, event won't be drawn
        self.auto = auto  # If true, event triggers automatically on collision
        self.frame_index = 0
        self.animation_frames = []
        # Visual feedback
        self.show_prompt = False
        self.collision_active = False

        # --- Load image instead of using blank circles ---
        if animated:
            try:
                self.animation_frames = load_horizontal_animation_sheet(resource_path(f'graphics/events/event_sheet.png'), frame_width=32, frame_height=32)
                self.base_image = self.animation_frames[0]
                self.image = pygame.transform.scale(self.base_image, (self.radius * 2, self.radius * 2))
                self.rect = self.image.get_rect(center=(self.x, self.y))
            except FileNotFoundError:
                self.image = None  # Fallback to blank draw if image not found
        else:
            try:
                self.base_image = pygame.image.load(resource_path(f'graphics\events\{event_id}.png')).convert_alpha()
                self.image = pygame.transform.scale(self.base_image, (self.radius * 2, self.radius * 2))
                self.rect = self.image.get_rect(center=(self.x, self.y))
            except FileNotFoundError:
                self.image = None  # Fallback to blank draw if image not found
        
    def check_collision(self, player):
        """Check if player is within trigger radius"""
        dx = player.x - self.x
        dy = player.y - self.y
        distance = sqrt(dx * dx + dy * dy)
        
        if distance <= self.trigger_radius:
            self.collision_active = True
            self.show_prompt = True
            return True
        else:
            self.collision_active = False
            self.show_prompt = False
            return False
    
    def trigger(self, player, story_manager):
        """
        Trigger the event - called when player presses interaction key
        Returns True if successfully triggered, False if already triggered
        """
        if self.triggered and self.trigger_once:
            return False
        
        self.triggered = True
        self.is_active = True
        
        # Trigger story event in story manager if event_id is set
        if self.event_id and story_manager:
            story_manager.trigger_story_event(self.event_id)
        
        print(f"Event '{self.name}' triggered!")
        
        if self.trigger_once:
            self.captured = True
        
        return True
    
    def auto_trigger(self, player, story_manager):
        """Auto-trigger when player enters radius (no button press needed)"""
        if not self.check_collision(player):
            return False
        
        return self.trigger(player, story_manager)
    
    def animate(self):  
        if self.animation_frames:
            self.frame_index = (self.frame_index + 0.15) % len(self.animation_frames)
            self.base_image = self.animation_frames[int(self.frame_index)] 

    def update(self):
        self.animate()
        self.pulse += 0.1
        if not self.captured and self.visible:
            scale = self.radius * 2 + sin(self.pulse) * 6
            self.image = pygame.transform.scale(self.base_image, (int(scale), int(scale)))
            self.rect = self.image.get_rect(center=(self.x, self.y))
        
    def draw(self, screen, camera_offset):
        if self.image is None:
            self.blank_draw(screen, camera_offset)
        else:
            self.image_draw(screen, camera_offset)

    def activate(self):
        """Legacy method - kept for compatibility"""
        self.is_active = True

    def blank_draw(self, screen, camera_offset):
        """Draw the event with camera offset"""
        if self.captured or not self.visible:
            return
            
        screen_x = self.x - camera_offset.x
        screen_y = self.y - camera_offset.y
        
        # Pulsing effect
        pulse_radius = self.radius + sin(self.pulse) * 5
        
        # Draw trigger radius if player is nearby
        if self.collision_active:
            trigger_surface = pygame.Surface((self.trigger_radius * 2, self.trigger_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(trigger_surface, (*self.color, 50), 
                             (self.trigger_radius, self.trigger_radius), self.trigger_radius)
            screen.blit(trigger_surface, (screen_x - self.trigger_radius, screen_y - self.trigger_radius))
        
        # Draw main event circle
        pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), int(pulse_radius))
        pygame.draw.circle(screen, 'white', (int(screen_x), int(screen_y)), int(pulse_radius), 2)
        
        # Draw name
        font = pygame.font.Font(None, 24)
        text = font.render(self.name, True, 'white')
        text_rect = text.get_rect(center=(screen_x, screen_y - 45))
        screen.blit(text, text_rect)
        
        # Draw interaction prompt
        if self.show_prompt and not self.triggered:
            prompt_font = pygame.font.Font(None, 20)
            prompt_text = prompt_font.render("Press E to interact", True, 'yellow')
            prompt_rect = prompt_text.get_rect(center=(screen_x, screen_y + 45))
            screen.blit(prompt_text, prompt_rect)

    def image_draw(self, screen, camera_offset):
        """Custom draw because you also want prompt + trigger radius"""
        if self.captured or not self.visible:
            return
            
        screen_x = self.x - camera_offset.x
        screen_y = self.y - camera_offset.y
        
        # Draw trigger radius if player is nearby
        if self.collision_active:
            trigger_surface = pygame.Surface((self.trigger_radius * 2, self.trigger_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(trigger_surface, (255, 255, 0, 50), 
                             (self.trigger_radius, self.trigger_radius), self.trigger_radius)
            screen.blit(trigger_surface, (screen_x - self.trigger_radius, screen_y - self.trigger_radius))
        
        # Draw main event image
        screen.blit(self.image, self.image.get_rect(center=(screen_x, screen_y)))
        
        # Draw name
        font = pygame.font.Font(None, 24)
        text = font.render(self.name, True, 'white')
        text_rect = text.get_rect(center=(screen_x, screen_y - 45))
        screen.blit(text, text_rect)
        
        # Draw interaction prompt
        if self.show_prompt and not self.triggered:
            prompt_font = pygame.font.Font(None, 20)
            prompt_text = prompt_font.render("Press E to interact", True, 'yellow')
            prompt_rect = prompt_text.get_rect(center=(screen_x, screen_y + 45))
            screen.blit(prompt_text, prompt_rect)