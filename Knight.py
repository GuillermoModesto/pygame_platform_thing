import pygame
from debug import debug

class Knight:
    """
    Player character with movement, animation, and collision handling.
    """
    
    def __init__(self, x, y, screen, world_rects):
        """
        Args:
            x, y: Starting position
            screen: Main display surface
            world_rects: List of collision rectangles from World
        """
        # Animation properties
        self.size = (14, 19)  # Original sprite size
        self.index = 0         # Current animation frame
        self.counter = 0       # Animation frame counter
        
        # Display properties
        self.screen = screen
        self.world_rects = world_rects
        
        # Load sprite sheets
        self.idle_sheet = pygame.image.load("img/knight/knight_idle_sheet.png").convert_alpha()
        self.run_sheet = pygame.image.load("img/knight/knight_run_sheet.png").convert_alpha()
        
        # Initialize sprite and rect
        self._init_sprite(x, y)
        
        # Movement properties
        self.vel_x = 0
        self.vel_y = 0
        self.sprinting = False
        self.moving = False
        self.jumped = False
        self.flipped = False  # For sprite direction
        self.was_sprinting_when_jumped = False  # Track sprint state at jump time
    
    def _init_sprite(self, x, y):
        """Initialize the sprite image and rect."""
        aux = self.idle_sheet.subsurface(0, 0, self.size[0], self.size[1])
        self.image = pygame.transform.scale(aux, (self.size[0]*3.5, self.size[1]*3.5))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def update(self, cam_offset_x, cam_offset_y, world_limit):
        """
        Main update method called each frame.
        
        Args:
            cam_offset_x, cam_offset_y: Camera position
            world_limit: Right boundary of the world
        """
        key = pygame.key.get_pressed()
        
        # Handle animations based on movement
        if key[pygame.K_a] or key[pygame.K_d]:
            self.animate(self.run_sheet, 16, 8)  # Run animation
        else:
            self.animate(self.idle_sheet, 4, 10)  # Idle animation
        
        # Movement and physics
        self._handle_movement(key)
        self._apply_gravity()
        self._handle_collisions()
        
        # Update position with world boundaries
        self._clamp_position(world_limit)
        
        # Render player
        self.screen.blit(self.image, (self.rect.x - cam_offset_x, self.rect.y - cam_offset_y))
    
    def _handle_movement(self, key):
        """Process keyboard input for movement."""
        # Horizontal movement
        self._move_x(key, increment=0.5, max_vel_x=7.5, 
                    sprint_inc_mod=1.7, sprint_max_mod=1.7)
        
        # Apply friction when on ground
        if not self.jumped:
            self._apply_friction(key, amount=1.3)
        
        # Jumping
        if key[pygame.K_SPACE] and not self.jumped:
            self.vel_y = -20
            self.jumped = True
    
    def _move_x(self, key, increment, max_vel_x, sprint_inc_mod, sprint_max_mod):
        """Handle horizontal movement with special air sprint rules."""
        was_sprinting = self.sprinting
        self.sprinting = key[pygame.K_LSHIFT]
        
        # Only apply deceleration if grounded
        if not self.jumped:
            # If we just stopped sprinting while grounded, store speed ratio
            if was_sprinting and not self.sprinting:
                self.sprint_decel_ratio = abs(self.vel_x) / (max_vel_x * sprint_max_mod)
            
            # Adjust movement parameters if sprinting
            if self.sprinting:
                max_vel_x *= sprint_max_mod
                increment *= sprint_inc_mod
            # Gradually return to normal speed when not sprinting (ground only)
            elif hasattr(self, 'sprint_decel_ratio'):
                decel_factor = 0.99  # 1% reduction per frame
                current_target = max_vel_x * self.sprint_decel_ratio
                if abs(self.vel_x) > current_target:
                    self.vel_x *= decel_factor
                    self.sprint_decel_ratio *= decel_factor
                else:
                    del self.sprint_decel_ratio
        else:
            # In air - maintain sprint speed if we were sprinting when we jumped
            if hasattr(self, 'was_sprinting_when_jumped'):
                if self.was_sprinting_when_jumped:
                    max_vel_x *= sprint_max_mod
                    increment *= sprint_inc_mod
        
        # Left movement
        if key[pygame.K_a]:
            target_vel = -max_vel_x
            if not self.sprinting and hasattr(self, 'sprint_decel_ratio') and not self.jumped:
                target_vel *= self.sprint_decel_ratio
            self.vel_x = max(target_vel, self.vel_x - increment)
            self.flipped = True
        
        # Right movement
        if key[pygame.K_d]:
            target_vel = max_vel_x
            if not self.sprinting and hasattr(self, 'sprint_decel_ratio') and not self.jumped:
                target_vel *= self.sprint_decel_ratio
            self.vel_x = min(target_vel, self.vel_x + increment)
            self.flipped = False
        
        # Track if we were sprinting at jump time
        if key[pygame.K_SPACE] and not self.jumped:
            self.was_sprinting_when_jumped = self.sprinting
        
        debug(f"Sprint:{self.sprinting}, Max:{max_vel_x}, Inc:{increment}, Vel:{self.vel_x}")
    
    def _apply_friction(self, key, amount):
        """Slow down horizontal movement when no keys are pressed."""
        if not (key[pygame.K_a] or key[pygame.K_d]):
            if self.vel_x > 0:
                self.vel_x = max(0, self.vel_x - amount)
            elif self.vel_x < 0:
                self.vel_x = min(0, self.vel_x + amount)
    
    def _apply_gravity(self, terminal_velocity=30, gravity=1):
        """Apply gravity with terminal velocity."""
        if self.vel_y < terminal_velocity:
            self.vel_y += gravity
    
    def _handle_collisions(self):
        """Resolve collisions with world tiles."""
        for tile in self.world_rects:
            # Horizontal collision
            if tile.colliderect(self.rect.x + self.vel_x, self.rect.y, self.rect.width, self.rect.height):
                if self.vel_x > 0:  # Moving right
                    self.vel_x = tile.left - self.rect.right
                elif self.vel_x < 0:  # Moving left
                    self.vel_x = tile.right - self.rect.left
            
            # Vertical collision
            if tile.colliderect(self.rect.x, self.rect.y + self.vel_y, self.rect.width, self.rect.height):
                if self.vel_y > 0:  # Falling
                    self.vel_y = tile.top - self.rect.bottom
                    self.jumped = False
                elif self.vel_y < 0:  # Jumping
                    self.vel_y = tile.bottom - self.rect.top
    
    def _clamp_position(self, world_limit):
        """Keep player within world boundaries."""
        self.rect.x = max(0, min(self.rect.x + self.vel_x, world_limit - self.rect.width))
        self.rect.y += self.vel_y
    
    def animate(self, sprite_sheet, steps, anim_cooldown):
        """
        Update sprite animation.
        
        Args:
            sprite_sheet: Source image containing animation frames
            steps: Number of frames in animation
            anim_cooldown: Frames between animation updates
        """
        self.counter += 1
        
        if self.counter > anim_cooldown:
            self.counter = 0
            self.index = (self.index + 1) % steps
            
            # Get current frame
            aux = sprite_sheet.subsurface(
                self.index * self.size[0], 0, 
                self.size[0], self.size[1])
            
            # Flip if facing left
            if self.flipped:
                aux = pygame.transform.flip(aux, True, False)
            
            # Scale and update image
            self.image = pygame.transform.scale(
                aux, 
                (self.size[0]*3.5, self.size[1]*3.5))