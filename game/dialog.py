import pygame
from settings import *
import state
from utility import resource_path  

class StoryManager:
    def __init__(self, level):
        self.level = level
        self.dialog_box = DialogBox()
        
        # Story state tracking
        self.story_flags = {}
        self.current_chapter = 0
        self.story_events = {}
        
        # Initialize story content
        self.setup_story()
    
    def setup_story(self):
        """
        Define all story content and progression
        
        ADD NEW STORY EVENTS HERE
        """
        
        self.story_events = {
            # Auto-triggered story events (based on conditions)
            'intro': {
                'condition': lambda: not self.story_flags.get('intro_seen', False),
                'speaker': None,
                'on_trigger': self.play_intro,
                'text': [],
                'on_complete': lambda: self.set_flag('intro_seen', True),
                'once': True
            },
            'events_seen': {
                'condition': lambda: self.story_flags.get('events_seen', 0) >= 5,
                'speaker': "Aether",
                'on_trigger': self.display_end_scene,
                'text': [],
                'on_complete': None,
                'once': True
            },
            
            # NEW: Events triggered by Event objects in the world
            'mysterious_beacon': {
                'condition': lambda: False,  # Manually triggered, not auto-checked
                'speaker': "Unknown Signal",
                'text': [
                    "...[STATIC]... is anyone out there?",
                    "This is Outpost Seven... we're under attack...",
                    "Please... send help... [SIGNAL LOST]"
                ],
                'on_complete': lambda: self.set_flag('beacon_found', True),  # Reward player with extra bullet
                'once': True
            },

            'power_up': {
                'condition': lambda: False,  # Manually triggered, not auto-checked
                'speaker': "Unknown Signal",
                'on_trigger': self.increase_player_bullets,
                'text': [
                    'Number of bullets increased!'
                ],
                'on_complete': None,
                'once': True
            },
            'health': {
                'condition': lambda: False,  # Manually triggered, not auto-checked
                'speaker': "Unknown Signal",
                'on_trigger': self.restore_player_health,
                'text': [],
                'on_complete': None,
                'once': True
            },
            'speed_up': {
                'condition': lambda: False,  # Manually triggered, not auto-checked
                'speaker': "Unknown Signal",
                'on_trigger': self.increase_player_speed,
                'text': [
                    'Speed increased!'
                ],
                'on_complete': None,
                'once': True
            },
            'chapter_1_start': {
                'condition': lambda: False,
                'speaker': "Aether",
                'text': ['check out the sun'],
                'on_complete': lambda: self.set_flag('chapter_1_started', True),
                'once': True
                },
            'solar_flares': {
                'condition': lambda: False,
                'speaker': "Aether",
                'on_trigger': self.display_solar_flares,
                'text': [],
                'on_complete': None,
                'once': False
                },
            'geomagnetic_storms': {
                'condition': lambda: False,
                'speaker': "Aether",
                'on_trigger': self.display_geomagnetic_storms,
                'text': [],
                'on_complete': None,
                'once': True
                },
            'ionosphere_disturbances': {
                'condition': lambda: False,
                'speaker': "Aether",
                'on_trigger': self.display_ionosphere_disturbances,
                'text': [],
                'on_complete': None,
                'once': True
                },
            'solar_energetic_particles': {
                'condition': lambda: False,
                'speaker': "Aether",
                'on_trigger': self.display_solar_particles,
                'text': [],
                'on_complete': None,
                'once': True
                },
            'cosmic_rays': {
                'condition': lambda: False,
                'speaker': "Aether",
                'on_trigger': self.display_cosmic_rays,
                'text': [],
                'on_complete': None,
                'once': True
                },
        }
    
    def set_flag(self, flag_name, value):
        """Set a story flag"""
        self.story_flags[flag_name] = value
        print(f"Story flag set: {flag_name} = {value}")
    
    def get_flag(self, flag_name, default=False):
        """Get a story flag value"""
        return self.story_flags.get(flag_name, default)

    def increment_flag(self, flag_name, amount=1):
        """Increment a numeric flag"""
        current = self.story_flags.get(flag_name, 0)
        self.story_flags[flag_name] = current + amount
    def increment_events_seen(self):
        """Increment the count of events seen"""
        self.increment_flag('events_seen', 1)
        print(f"Events seen incremented to {self.get_flag('events_seen')}")
    def complete_chapter(self, chapter_number):
        """Mark a chapter as complete"""
        self.set_flag(f'chapter_{chapter_number}_complete', True)
        self.current_chapter = chapter_number
        print(f"Chapter {chapter_number} complete!")
    
    def check_story_events(self):
        """Check all story events and trigger appropriate ones"""
        if self.dialog_box.active:
            return
        
        for event_id, event_data in self.story_events.items():
            if event_data['condition']():
                self.trigger_story_event(event_id)
                break
    
    def trigger_story_event(self, event_id):
        """Trigger a specific story event"""
        if event_id not in self.story_events:
            print(f"Warning: Story event '{event_id}' not found!")
            return
        
        event_data = self.story_events[event_id]
        
        event_data['on_trigger']() if 'on_trigger' in event_data and event_data['on_trigger'] else None
        if not 'text' in event_data or not event_data['text']:
            print(f"Warning: Story event '{event_id}' has no text defined!")
        else:
            self.dialog_box.show_dialog(
                speaker=event_data['speaker'],
                text_lines=event_data['text'],
                on_complete=event_data.get('on_complete', None) if 'on_complete' in event_data and event_data['on_complete'] else None
            )
    def trigger_quiz_state(self):
        state.PLAY_STATE = state.PlayState.QUIZ

    # NEW: Helper methods for event callbacks
    def play_intro(self):
        self.dialog_box.show_dialog(
            speaker=['Nasa Mission Control']*6 + ['Aether']*6,
            text_lines=[
                'Young astronaut, do you copy?',
                '… Good, we hear you loud and clear.',
                'Your mission is to explore our solar system and study the strange and powerful forces we call Space Weather.',
                'Each discovery you make will bring us closer to understanding how these cosmic storms shape our world.',
                'When your journey ends, we’ll ask you what you’ve learned.',
                'The knowledge you gather may guide the future of humanity. We’re counting on you. Mission Control, out.',
                'Ahh… so you are the one they send among the stars.',
                'Welcome, child of starlight. I am Aether, the Phoenix who soars through storms and fire.',
                'Beware, traveler, strange vessels, unfriendly and unknown, roam these skies. Keep your wits about you.',
                'But fear not. To uncover the secrets of space weather, you need only seek them out.',
                'Draw near to each phenomenon, and I shall share their stories with you.',
                'Now, spread your wings, little one, the cosmos awaits.'
            ],
            voice_lines=[resource_path('sound/mission_control_1.mp3'),resource_path('sound/mission_control_2.mp3'),
                         resource_path('sound/mission_control_3.mp3'),resource_path('sound/mission_control_4.mp3'),
                         resource_path('sound/mission_control_5.mp3'),resource_path('sound/mission_control_6.mp3'),
                         resource_path('sound/aether_meet_1.mp3'),resource_path('sound/aether_meet_2.mp3'),
                         resource_path('sound/aether_meet_3.mp3'),resource_path('sound/aether_meet_4.mp3'),
                         resource_path('sound/aether_meet_5.mp3'),resource_path('sound/aether_meet_6.mp3')],
            icons= [resource_path('graphics/icons/charlie.png')]*6 + [resource_path('graphics/icons/aether_closed.png')]*6,
            on_complete= lambda: self.set_flag('intro_seen', True),
        )
    def display_end_scene(self):
        self.dialog_box.show_dialog(
            speaker="Aether",
            text_lines=[
                "You have gazed upon many wonders of the cosmos, child of starlight… Now, let us see what you have learned. ",
                "The stars whisper their questions—are you ready to answer them?"
            ],
            voice_lines=[resource_path('sound/aether_end_1.mp3'),resource_path('sound/aether_end_2.mp3')],
            icons=[resource_path('graphics/icons/aether_closed.png')]*2,
            on_complete=self.trigger_quiz_state,
        )
    def display_solar_flares(self):
        """Display a video or GIF of the sun in the dialog box"""
        self.dialog_box.show_dialog(
            speaker="Aether",
            text_lines=[
                'Behold, traveler… the Sun flares in fury. A solar flare is a sudden burst of light and energy, born from her tangled magnetic threads.',
                'These sparks can trouble our machines, yet they also paint the skies with shimmering auroras.',
                'The greater the flare, the mightier its roar.'
            ],
            voice_lines=[resource_path('sound/solar_flare_1.mp3'),resource_path('sound/solar_flare_2.mp3'),
                         resource_path('sound/solar_flare_3.mp3')],
            icons=[resource_path('graphics/icons/aether_closed.png')]*3,
            on_complete=self.increment_events_seen,
            show_video=True,
            video_path=resource_path("graphics/gifs/solar_flares.gif") # Path to your video or GIF file
        )

    def display_geomagnetic_storms(self):
        self.dialog_box.show_dialog(
            speaker="Aether",
            text_lines=[
                'When the solar wind strikes with great force, Earth’s shield — the magnetosphere — trembles. ',
                'This geomagnetic storm stirs the space around our world… and paints the skies with dancing lights we call auroras.'
            ],
            voice_lines=[resource_path('sound/geomagnetic_storms_1.mp3'),resource_path('sound/geomagnetic_storms_2.mp3')],
            icons=[resource_path('graphics/icons/aether_closed.png')]*2,
            on_complete=self.increment_events_seen,
            show_video=True,
            video_path=resource_path("graphics/gifs/aurora.gif")
        )
    def display_solar_particles(self):
        self.dialog_box.show_dialog(
            speaker="Aether",
            text_lines=[
                'The Sun sometimes casts out swift, invisible sparks — Solar Energetic Particles',
                'Born from great flares and fiery waves, they race through space with power enough to harm both traveler and machine.',
                'Some strike quickly, others linger like long storms… but by studying them, we learn the moods of our star.'
            ],
            voice_lines=[resource_path('sound/solar_particles_1.mp3'),resource_path('sound/solar_particles_2.mp3'),
                         resource_path('sound/solar_particles_3.mp3')],
            icons=[resource_path('graphics/icons/aether_closed.png')]*3,
            on_complete=self.increment_events_seen,
            show_video=True,
            video_path=resource_path("graphics/gifs/solar_energetic_particles.gif") 
        )
    def display_ionosphere_disturbances(self):
        self.dialog_box.show_dialog(
            speaker="Aether",
            text_lines=[
                'High above Earth lies the ionosphere — a sea of charged particles.',
                'At times it stirs with sudden waves and irregular storms, born from solar flares, geomagnetic tempests, or even great quakes below.',
                'These disturbances can bend radio voices, twist satellite paths, and confuse the guiding hand of GPS',
                '… a reminder that even the sky itself can tremble.'
            ],
            voice_lines=[resource_path('sound/ionosphere_1.mp3'),resource_path('sound/ionosphere_2.mp3'),
                         resource_path('sound/ionosphere_3.mp3'), resource_path('sound/ionosphere_4.mp3')],
            icons=[resource_path('graphics/icons/aether_closed.png')]*4,
            on_complete=self.increment_events_seen,
            show_video=True,
            video_path=resource_path("graphics/gifs/ionospheric_disturbances.gif") 
        )
    def display_cosmic_rays(self):
        self.dialog_box.show_dialog(
            speaker="Aether",
            text_lines=[
                'From beyond our Sun, born of ancient supernovae, come the Galactic Cosmic Rays — fragments of stars, stripped of their electrons, racing near the speed of light.',
                'They are powerful wanderers, shaped by magnetic fields, yet dangerous to travelers… for they carry the deep scars of the galaxy’s most violent storms.'
            ],
            voice_lines=[resource_path('sound/cosmic_rays_1.mp3'),resource_path('sound/cosmic_rays_2.mp3')],
            icons=[resource_path('graphics/icons/aether_closed.png')]*3,
            on_complete=self.increment_events_seen,
            show_video=True,
            video_path=resource_path("graphics/gifs/cosmic_rays.gif")
        )
    
    def restore_player_health(self):
        """Restore player to full health"""
        if hasattr(self.level, 'player'):
            self.level.player.health += 30
            print("Health restored!")
    def increase_player_bullets(self):
        """Increment player's bullets by 1"""
        if hasattr(self.level, 'player'):
            self.level.player.bullets += 1
            print("Player bullets increased!")
    def increase_player_speed(self):
        """Increase player speed"""
        if hasattr(self.level, 'player'):
            self.level.player.max_speed += 1.0
            print("Player speed increased!")
    def start_boss_fight(self):
        """Start a boss encounter"""
        self.set_flag('boss_fight_active', True)
        print("Boss fight started!")
        # You can add boss spawning logic here
    
    def on_enemy_killed(self):
        """Called when an enemy is killed"""
        self.increment_flag('enemies_killed', 1)
    
    def handle_events(self, event):
        """Handle pygame events"""
        if self.dialog_box.handle_input(event):
            return True
        return False
    
    def update(self):
        """Update story system"""
        self.dialog_box.update()
        self.check_story_events()
    
    def draw(self):
        """Draw story UI"""
        self.dialog_box.draw()

import pygame

class DialogBox:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, 28)
        self.title_font = pygame.font.Font(None, 36)
        
        # Dialog box properties
        self.active = False
        self.current_text = ""
        self.current_speaker = ""
        self.text_lines = []
        self.current_line_index = 0
        
        # Speaker properties
        self.speakers = []
        
        # Voice line properties
        self.voice_lines = []
        self.current_voice = None
        
        # Icon properties
        self.icons = []
        self.current_icon = None
        
        # Visual properties
        self.box_width = 800
        self.box_height = 200
        self.box_x = (self.display_surface.get_width() - self.box_width) // 2
        self.box_y = self.display_surface.get_height() - self.box_height - 50
        self.padding = 20

        # Portrait box
        self.portrait_size = 128
        self.portrait_padding = 15
        self.portraits = {
            # Example:
            # "Alice": pygame.image.load("alice.png").convert_alpha(),
        }
        self.blank_portrait = pygame.Surface((self.portrait_size, self.portrait_size))
        self.blank_portrait.fill((50, 50, 50))  # gray placeholder

        # Text animation
        self.char_index = 0
        self.text_speed = 2  # characters per frame
        self.display_text = ""
        self.text_complete = False
        
        # Callback for when dialog finishes
        self.on_complete_callback = None
        
        self.show_video = False
        self.video_path = None
        self.video_frames = []
        self.current_frame_index = 0
        self.frame_delay = 100  # milliseconds between frames
        self.last_frame_time = 0
        self.video_surface = None
        
        # Video box properties (takes up space above dialog box)
        self.video_box_padding = 20
        self.video_box_height = self.display_surface.get_height() - self.box_height - 100
        self.video_box_width = self.box_width
        self.video_box_x = self.box_x
        self.video_box_y = 50
        
    def _load_video_or_gif(self, video_path):
        """Load video or GIF frames"""
        try:
            # Try loading as GIF using PIL if available
            try:
                from PIL import Image
                gif = Image.open(video_path)
                self.video_frames = []
                
                # Extract all frames from GIF
                try:
                    while True:
                        # Convert PIL image to pygame surface
                        frame = gif.convert('RGBA')
                        pygame_image = pygame.image.fromstring(
                            frame.tobytes(), frame.size, frame.mode
                        )
                        self.video_frames.append(pygame_image)
                        gif.seek(gif.tell() + 1)
                except EOFError:
                    pass  # End of GIF frames
                    
                # Get frame delay from GIF info
                if hasattr(gif, 'info') and 'duration' in gif.info:
                    self.frame_delay = gif.info['duration']
                    
            except ImportError:
                # PIL not available, try loading as static image
                image = pygame.image.load(video_path).convert_alpha()
                self.video_frames = [image]
                
        except Exception as e:
            print(f"Error loading video/GIF: {e}")
            # Create a placeholder surface
            placeholder = pygame.Surface((400, 300))
            placeholder.fill((50, 50, 50))
            font = pygame.font.Font(None, 24)
            text = font.render("Video not found", True, (200, 200, 200))
            text_rect = text.get_rect(center=(200, 150))
            placeholder.blit(text, text_rect)
            self.video_frames = [placeholder]
    
    def _play_voice_line(self, voice_path):
        """Play a voice line audio file"""
        if voice_path is None:
            return
            
        try:
            # Stop current voice if playing
            if self.current_voice and pygame.mixer.get_busy():
                pygame.mixer.stop()
            
            # Load and play new voice line
            self.current_voice = pygame.mixer.Sound(voice_path)
            self.current_voice.play()
        except Exception as e:
            print(f"Error playing voice line: {e}")
    
    def show_dialog(self, speaker, text_lines, voice_lines=None, icons=None, on_complete=None, show_video=False, video_path=None):
        """
        Show a dialog box with text
        
        Args:
            speaker: Name of who's speaking (string) or list of speaker names for each line
            text_lines: List of strings, each is one "page" of dialog
            voice_lines: List of audio file paths corresponding to each text_line (or None for no audio)
            icons: List of pygame Surfaces or image paths corresponding to each text_line (or None for default portrait)
            on_complete: Callback function to call when dialog finishes
            show_video: Boolean flag to show video/GIF box above dialog
            video_path: Path to video or GIF file (required if show_video is True)
        """
        self.active = True
        state.PLAY_STATE = state.PlayState.DIALOG
        self.text_lines = text_lines
        
        # Handle speaker - can be string or list
        if isinstance(speaker, str):
            # Fill speakers list with the same speaker for all lines
            self.speakers = [speaker] * len(text_lines)
        elif isinstance(speaker, list):
            # Copy the list of speakers
            self.speakers = speaker.copy()
        else:
            # Fallback to empty string if speaker is None or invalid
            self.speakers = [""] * len(text_lines)
        
        # Initialize current speaker
        self.current_speaker = self.speakers[0] if self.speakers else ""
        
        self.voice_lines = voice_lines if voice_lines else [None] * len(text_lines)
        
        # Process icons - can be Surfaces or file paths
        if icons:
            self.icons = []
            for icon in icons:
                if icon is None:
                    self.icons.append(None)
                elif isinstance(icon, str):
                    # Load image from path
                    try:
                        loaded_icon = pygame.image.load(icon).convert_alpha()
                        self.icons.append(loaded_icon)
                    except Exception as e:
                        print(f"Error loading icon {icon}: {e}")
                        self.icons.append(None)
                else:
                    # Assume it's already a Surface
                    self.icons.append(icon)
        else:
            self.icons = [None] * len(text_lines)
        
        self.current_line_index = 0
        self.char_index = 0
        self.display_text = ""
        self.text_complete = False
        self.on_complete_callback = on_complete
        
        # Load video once at the start if enabled
        if show_video and video_path:
            self.show_video = True
            self.video_path = video_path
            self._load_video_or_gif(self.video_path)
            self.current_frame_index = 0
            self.last_frame_time = pygame.time.get_ticks()
        else:
            self.show_video = False
            self.video_frames = []
        
        if self.text_lines:
            self.current_text = self.text_lines[0]
            # Play the first voice line
            if self.voice_lines and len(self.voice_lines) > 0:
                self._play_voice_line(self.voice_lines[0])
            # Set the first icon
            if self.icons and len(self.icons) > 0:
                self.current_icon = self.icons[0]
    
    def handle_input(self, event):
        """Handle keyboard input for advancing dialog"""
        if not self.active:
            return False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.text_complete:
                    # Move to next line
                    self.current_line_index += 1
                    
                    if self.current_line_index >= len(self.text_lines):
                        # Dialog finished
                        self.active = False
                        state.PLAY_STATE = state.PlayState.PLAY
                        self.show_video = False
                        self.video_frames = []
                        self.current_frame_index = 0
                        # Stop any playing voice
                        if pygame.mixer.get_busy():
                            pygame.mixer.stop()
                        if self.on_complete_callback:
                            self.on_complete_callback()
                        return True
                    else:
                        # Load next line
                        self.current_text = self.text_lines[self.current_line_index]
                        self.char_index = 0
                        self.display_text = ""
                        self.text_complete = False
                        
                        # Update speaker for this line
                        if self.current_line_index < len(self.speakers):
                            self.current_speaker = self.speakers[self.current_line_index]
                        
                        # Play corresponding voice line
                        if self.current_line_index < len(self.voice_lines):
                            self._play_voice_line(self.voice_lines[self.current_line_index])
                        
                        # Set corresponding icon
                        if self.current_line_index < len(self.icons):
                            self.current_icon = self.icons[self.current_line_index]
                else:
                    # Skip text animation, show full text immediately
                    self.display_text = self.current_text
                    self.char_index = len(self.current_text)
                    self.text_complete = True
                return True
        
        return False
    
    def update(self):
        """Update text animation and video frames"""
        if not self.active:
            return
        
        # Animate text appearance
        if not self.text_complete:
            if self.char_index < len(self.current_text):
                self.char_index += self.text_speed
                if self.char_index > len(self.current_text):
                    self.char_index = len(self.current_text)
                self.display_text = self.current_text[:int(self.char_index)]
            else:
                self.text_complete = True
        
        # Animate video if enabled (loops continuously)
        if self.show_video and self.video_frames:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_frame_time >= self.frame_delay:
                self.current_frame_index = (self.current_frame_index + 1) % len(self.video_frames)
                self.last_frame_time = current_time
    
    def draw(self):
        """Draw the dialog box and optional video box"""
        if not self.active:
            return
        
        # Draw semi-transparent background overlay
        overlay = pygame.Surface(self.display_surface.get_size())
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.display_surface.blit(overlay, (0, 0))
        
        if self.show_video and self.video_frames:
            # Draw video box background
            video_box_rect = pygame.Rect(
                self.video_box_x, 
                self.video_box_y, 
                self.video_box_width, 
                self.video_box_height
            )
            pygame.draw.rect(self.display_surface, (10, 10, 20), video_box_rect)
            pygame.draw.rect(self.display_surface, (100, 150, 200), video_box_rect, 3)
            
            # Draw current video frame (scaled to fit)
            if self.current_frame_index < len(self.video_frames):
                current_frame = self.video_frames[self.current_frame_index]
                
                # Scale frame to fit video box while maintaining aspect ratio
                frame_rect = current_frame.get_rect()
                scale_x = (self.video_box_width - self.video_box_padding * 2) / frame_rect.width
                scale_y = (self.video_box_height - self.video_box_padding * 2) / frame_rect.height
                scale = min(scale_x, scale_y)
                
                new_width = int(frame_rect.width * scale)
                new_height = int(frame_rect.height * scale)
                scaled_frame = pygame.transform.scale(current_frame, (new_width, new_height))
                
                # Center the frame in the video box
                frame_x = self.video_box_x + (self.video_box_width - new_width) // 2
                frame_y = self.video_box_y + (self.video_box_height - new_height) // 2
                
                self.display_surface.blit(scaled_frame, (frame_x, frame_y))
        
        # Draw dialog box background
        box_rect = pygame.Rect(self.box_x, self.box_y, self.box_width, self.box_height)
        pygame.draw.rect(self.display_surface, (20, 20, 40), box_rect)
        pygame.draw.rect(self.display_surface, (100, 150, 200), box_rect, 3)

        # --- Portrait box ---
        portrait_x = self.box_x - self.portrait_size - self.portrait_padding
        portrait_y = self.box_y + (self.box_height - self.portrait_size) // 2
        
        # Use current icon if available, otherwise use speaker portrait or blank
        if self.current_icon is not None:
            # Scale icon to fit portrait size
            icon_scaled = pygame.transform.scale(self.current_icon, (self.portrait_size, self.portrait_size))
            self.display_surface.blit(icon_scaled, (portrait_x, portrait_y))
        else:
            speaker_image = self.portraits.get(self.current_speaker, self.blank_portrait)
            self.display_surface.blit(speaker_image, (portrait_x, portrait_y))
        
        pygame.draw.rect(self.display_surface, (100, 150, 200),
                         (portrait_x, portrait_y, self.portrait_size, self.portrait_size), 2)
        
        # Draw speaker name if present
        if self.current_speaker:
            speaker_surf = self.title_font.render(self.current_speaker, True, (200, 200, 255))
            self.display_surface.blit(speaker_surf, 
                                     (self.box_x + self.padding, 
                                      self.box_y + self.padding))
            text_y_offset = 45
        else:
            text_y_offset = self.padding
        
        # Draw text (word wrap)
        words = self.display_text.split(' ')
        lines = []
        current_line = ""
        max_width = self.box_width - (self.padding * 2)
        
        for word in words:
            test_line = current_line + word + " "
            test_surf = self.font.render(test_line, True, (255, 255, 255))
            
            if test_surf.get_width() <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word + " "
        
        if current_line:
            lines.append(current_line)
        
        # Draw each line
        for i, line in enumerate(lines):
            line_surf = self.font.render(line, True, (255, 255, 255))
            self.display_surface.blit(line_surf,
                                     (self.box_x + self.padding,
                                      self.box_y + text_y_offset + (i * 30)))
        
        # Draw continue indicator
        if self.text_complete:
            indicator_text = "Press Enter to continue" if self.current_line_index < len(self.text_lines) - 1 else "Press Enter to close"
            indicator_surf = self.font.render(indicator_text, True, (150, 150, 150))
            self.display_surface.blit(indicator_surf,
                                     (self.box_x + self.box_width - indicator_surf.get_width() - self.padding,
                                      self.box_y + self.box_height - 30))