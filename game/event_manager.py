# ============================================================================
# event_manager.py - NEW FILE: EVENT MANAGER CLASS
# ============================================================================
import pygame
from event import Event
from math import cos, sin, pi

class EventManager:
    """Manages all events in the game - handles creation, templates, and patterns"""
    
    def __init__(self, level):
        self.level = level
        self.events = []
        self.event_templates = {}
        self.setup_templates()
    
    def setup_templates(self):
        """
        Define event templates for reusability
        
        ADD NEW TEMPLATES HERE:
        Each template needs: name, info, color, trigger_radius
        """
        self.event_templates = {
            'activation_area':{
                'name': 'Activation Area',
                'info': 'Activate a story event',
                'color': (255, 100, 100),
                'trigger_radius': 400
            },
            'power_up': {
                'name': 'Power-Up',
                'info': 'Increases Number of Bullets',
                'color': (255, 100, 100),
                'trigger_radius': 50
            },
            'health': {
                'name': 'Health Pack',
                'info': 'Heals 50 Health',
                'color': (255, 100, 100),
                'trigger_radius': 50
            },
            'speed_up': {
                'name': 'Speed Boost',
                'info': 'Increases Speed',
                'color': (255, 100, 100),
                'trigger_radius': 50
            },
        }
    
    def create_event(self, template_name, x, y, event_id=None, visible=True, auto=False, animated = False, **overrides):
        """
        Create an event from a template
        
        Args:
            template_name: Name of template to use (e.g., 'beacon', 'ruins')
            x, y: World position
            event_id: Story event ID to trigger
            visible: Whether the event is visible
            auto: Whether the event auto-triggers (no E press needed)
            **overrides: Any properties to override from template (e.g., name='Custom Name')
        
        Returns:
            The created Event object
        """
        if template_name not in self.event_templates:
            print(f"Warning: Template '{template_name}' not found")
            return None
        
        # Get template and apply overrides
        template = self.event_templates[template_name].copy()
        template.update(overrides)
        
        if event_id is not None:
            event_name_safe = event_id.split('_')
            event_name = ' '.join(word.capitalize() for word in event_name_safe)
        # Create event
        event = Event(
            x=x, y=y,
            groups=[],
            name=event_name,
            info=template['info'],
            color=template['color'],
            event_id=event_id,
            visible=visible,
            auto=auto,
            animated=animated
        )
        event.trigger_radius = template['trigger_radius']
        
        # Add to level
        self.level.add_to_chunk(event, x, y)
        self.level.events.append(event)
        self.events.append(event)
        
        return event
    
    def create_event_chain(self, positions, template_name, base_event_id, visible=True, auto=False, **template_overrides):
        """
        Create a chain of similar events
        
        Args:
            positions: List of (x, y) tuples
            template_name: Template to use
            base_event_id: Base name for event IDs (will append _0, _1, etc.)
            visible: Whether events are visible
            auto: Whether events auto-trigger
        
        Returns:
            List of created events
        """
        created_events = []
        for i, (x, y) in enumerate(positions):
            event_id = f"{base_event_id}_{i}"
            event = self.create_event(
                template_name, x, y, event_id,
                name=f"{self.event_templates[template_name]['name']} {i+1}",
                visible=visible,
                auto=auto,
                **template_overrides
            )
            created_events.append(event)
        return created_events
    
    def create_circular_pattern(self, center_x, center_y, radius, count, template_name, base_event_id, auto=False):
        """
        Create events in a circular pattern around a center point
        
        Args:
            center_x, center_y: Center of the circle
            radius: Radius of the circle
            count: Number of events to create
            template_name: Template to use
            base_event_id: Base name for event IDs
            auto: Whether events auto-trigger
        """
        positions = []
        for i in range(count):
            angle = (2 * pi * i) / count
            x = center_x + radius * cos(angle)
            y = center_y + radius * sin(angle)
            positions.append((x, y))
        
        return self.create_event_chain(positions, template_name, base_event_id, auto=auto)
    
    def create_grid_pattern(self, start_x, start_y, rows, cols, spacing, template_name, base_event_id, auto=False):
        """
        Create events in a grid pattern
        
        Args:
            start_x, start_y: Top-left corner of grid
            rows, cols: Grid dimensions
            spacing: Distance between events
            template_name: Template to use
            base_event_id: Base name for event IDs
            auto: Whether events auto-trigger
        """
        positions = []
        for row in range(rows):
            for col in range(cols):
                x = start_x + (col * spacing)
                y = start_y + (row * spacing)
                positions.append((x, y))
        
        return self.create_event_chain(positions, template_name, base_event_id, auto=auto)
    
    def create_line_pattern(self, start_x, start_y, end_x, end_y, count, template_name, base_event_id, visible=True, auto=False):
        """
        Create events in a line from start to end
        
        Args:
            start_x, start_y: Starting position
            end_x, end_y: Ending position
            count: Number of events to place
            template_name: Template to use
            base_event_id: Base name for event IDs
            visible: Whether events are visible
            auto: Whether events auto-trigger
        """
        positions = []
        for i in range(count):
            t = i / (count - 1) if count > 1 else 0
            x = start_x + (end_x - start_x) * t
            y = start_y + (end_y - start_y) * t
            positions.append((x, y))
        
        return self.create_event_chain(positions, template_name, base_event_id, visible=visible, auto=auto)
    
    # ========================================================================
    # EVENT INTERACTION LOGIC - Centralized event triggering
    # ========================================================================
    
    def check_event_collisions(self, player):
        """
        Check all events for collision and update their visual state
        Also auto-trigger events that have auto=True
        """
        for event in self.events:
            if event.captured:
                continue
            
            # Check if player is within trigger radius
            is_colliding = event.check_collision(player)
            
            # Auto-trigger if event has auto flag set
            if is_colliding and event.auto and not event.triggered:
                self.trigger_event(event, player)
    
    def check_manual_event_interaction(self, player):
        """
        Check if player pressed E near any manual-trigger events
        Called when player presses E key
        """
        for event in self.events:
            if event.captured or event.auto:  # Skip captured or auto events
                continue
            
            # Check if player is within trigger radius
            if event.check_collision(player):
                # Player is near event and pressed E
                self.trigger_event(event, player)
                break  # Only trigger one event at a time
    
    def trigger_event(self, event, player):
        """
        Centralized event triggering logic
        
        Args:
            event: The Event object to trigger
            player: The player object
        """
        # Check if event can be triggered
        if event.triggered and event.trigger_once:
            return False
        
        # Mark as triggered
        event.triggered = True
        event.is_active = True
        
        # Trigger story event in story manager if event_id is set
        if event.event_id and hasattr(self.level, 'story_manager') and self.level.story_manager:
            self.level.story_manager.trigger_story_event(event.event_id)
        
        print(f"Event '{event.name}' triggered! (auto={event.auto})")
        
        # Mark as captured if it's a one-time event
        if event.trigger_once:
            event.captured = True
        
        return True
    
    # ========================================================================
    # CHAPTER SETUP METHODS - ADD YOUR STORY EVENTS HERE
    # ========================================================================
    
    def setup_chapter_1_events(self):
        """
        Setup all events for Chapter 1
        
        MODIFY THIS METHOD TO ADD CHAPTER 1 EVENTS
        """
        print("Setting up Chapter 1 events...")
        
        self.create_event('activation_area', 5200, 7600, 'solar_flares', visible=True, auto=True, animated=True)
        self.create_event('activation_area', 5760, 7100, 'geomagnetic_storms', visible=True, auto=True, animated=True)
        self.create_event('activation_area', 2900, 4600, 'ionosphere_disturbances', visible=True, auto=True, animated=True)
        self.create_event('activation_area', 8800, 4600, 'solar_energetic_particles', visible=True, auto=True, animated=True)
        self.create_event('activation_area', 6300, 9600, 'cosmic_rays', visible=True, auto=True, animated=True)
        self.create_event('power_up', 7200, 6900, 'power_up', visible=True, auto=True)
        self.create_event('power_up', 7100, 9300, 'power_up', visible=True, auto=True)
        self.create_event('power_up', 3200, 8400, 'power_up', visible=True, auto=True)
        self.create_event('health', 4800, 6800, 'health', visible=True, auto=True)
        self.create_event('health', 5450, 8000, 'health', visible=True, auto=True)
        self.create_event('speed_up', 6000, 7500, 'speed_up', visible=True, auto=True)
        self.create_event('speed_up', 5200, 4000, 'speed_up', visible=True, auto=True)
        
        print(f"Chapter 1: Created {len(self.events)} events")
    
    def setup_chapter_2_events(self):
        """
        Setup all events for Chapter 2
        
        MODIFY THIS METHOD TO ADD CHAPTER 2 EVENTS
        """
        print("Setting up Chapter 2 events...")
        
        # Grid of beacons in a sector
        self.create_grid_pattern(2000, 2000, 3, 3, 500, 'beacon', 'sector_2_beacon')
        
        # Boss arena at the end (auto-trigger)
        self.create_event('boss_arena', 3500, 3500, 'chapter_2_boss',
                         name='Enemy Command Ship',
                         color=(255, 0, 0),
                         auto=True)
        
        print(f"Chapter 2: Created {len(self.events) - len([e for e in self.events if 'sector_2' not in str(e.event_id)])} new events")
    
    def setup_tutorial_events(self):
        """
        Setup tutorial events
        
        MODIFY THIS METHOD TO ADD TUTORIAL EVENTS
        """
        print("Setting up tutorial events...")
        
        # Tutorial waypoints in a line (auto-trigger for smooth tutorial)
        self.create_line_pattern(100, 100, 500, 500, 5, 'checkpoint', 'tutorial_waypoint', auto=True)
        
    def setup_custom_events(self):
        """
        Setup any custom one-off events
        
        ADD CUSTOM EVENTS HERE - EXAMPLES:
        """
        # Example: Create a single custom event with auto-trigger
        # self.create_event('station', 2500, 2500, 'trading_post',
        #                  name='Port Haven Station',
        #                  color=(180, 180, 80),
        #                  auto=False)
        
        # Example: Create events at specific locations
        # important_locations = [
        #     (1000, 500, 'first_contact'),
        #     (2000, 1500, 'derelict_ship'),
        #     (3000, 2000, 'asteroid_field')
        # ]
        # for x, y, event_id in important_locations:
        #     self.create_event('ruins', x, y, event_id, auto=True)
        
        pass
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def get_event_by_id(self, event_id):
        """Get an event by its story event ID"""
        for event in self.events:
            if event.event_id == event_id:
                return event
        return None
    
    def remove_event(self, event):
        """Remove an event from the game"""
        if event in self.events:
            self.events.remove(event)
        if event in self.level.events:
            self.level.events.remove(event)
        event.kill()
    
    def clear_all_events(self):
        """Remove all events (useful for chapter transitions)"""
        for event in self.events[:]:  # Copy list to avoid modification during iteration
            self.remove_event(event)
        self.events.clear()