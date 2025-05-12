import pygame

class Camera:
    """
    Handles camera movement to follow the player with smooth scrolling.
    Includes boundaries to prevent showing areas outside the world.
    """
    
    def __init__(self, player, screen_width, screen_height):
        """
        Args:
            player: The player object to follow
            screen_width, screen_height: Viewport dimensions
        """
        self.player = player
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Camera position with float precision for smooth movement
        self.offset = pygame.math.Vector2(0, 0)
        self.offset_float = pygame.math.Vector2(0, 0)
        
        # Camera follows player with this offset from screen center
        self.CONST = pygame.math.Vector2(
            -self.screen_width / 2 + player.rect.x / 4, 
            -player.rect.y)
    
    def scroll(self, left_border, right_border, top_border, bottom_border):
        """
        Update camera position while respecting world boundaries.
        Added smoothing to reduce jitter during jumps.
        """
        # Smoother camera follow with lerping
        target_x = self.player.rect.x + self.CONST.x
        target_y = self.player.rect.y + self.CONST.y
        
        # Use linear interpolation for smoother movement
        self.offset_float.x += (target_x - self.offset_float.x) * 0.1
        self.offset_float.y += (target_y - self.offset_float.y) * 0.1
        
        # Convert to integer for pixel-perfect rendering
        self.offset.x, self.offset.y = int(self.offset_float.x), int(self.offset_float.y)
        
        # Clamp camera position to world boundaries
        self.offset.x = max(left_border, self.offset.x)
        self.offset.x = min(self.offset.x, right_border - self.screen_width)
        self.offset.y = max(top_border, self.offset.y)
        self.offset.y = min(self.offset.y, bottom_border - self.screen_height)