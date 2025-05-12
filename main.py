import pygame
from World import World
from Knight import Knight
from Camera import Camera
from debug import debug
from psutil import Process, cpu_percent
from os import getpid

class Game:
    """
    Main game class that initializes and runs the game loop.
    """
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((900, 700))
        pygame.display.set_caption("Platformer")
        self.clock = pygame.time.Clock()
        
        # Performance monitoring
        self.cpu_usage = cpu_percent(interval=None)
        self.max_cpu_usage = self.cpu_usage
        self.cpu_update_interval = 1
        self.cpu_update_accumulator = 0
        
        # Game world setup
        self.tile_size = 50
        self.world = World(self.tile_size, self.screen)
        self.world_limit_x = len(self.world.data[0]) * self.tile_size
        self.world_limit_y = len(self.world.data) * self.tile_size
        
        # Player setup
        self.player = Knight(
            450, 
            self.screen.get_height() - 230, 
            self.screen, 
            self.world.rects)
        
        # Camera setup
        self.camera = Camera(
            self.player, 
            self.screen.get_width(), 
            self.screen.get_height())
    
    def run(self):
        """Main game loop."""
        running = True
        while running:
            running = self._handle_events()  # Update running state
            self._update()
            self._render()
            self._monitor_performance()
            
            pygame.display.update()
            self.clock.tick(60)
        
        pygame.quit()
    
    def _handle_events(self):
        """Process all pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Signal to exit game
        return True  # Continue running
    
    def _update(self):
        """Update game state."""
        self.world.display(self.camera.offset.x, self.camera.offset.y)
        self.player.update(
            self.camera.offset.x, 
            self.camera.offset.y, 
            self.world_limit_x)
        self.camera.scroll(
            0, self.world_limit_x, 
            0, self.world_limit_y)
    
    def _render(self):
        """Render debug information."""
        debug(f"FPS:{self.clock.get_fps():.2f}", x=810)
        debug(f"Memory:{Process(getpid()).memory_info().rss / 1024 ** 2:.2f} MB", 
              y=29, x=693)
    
    def _monitor_performance(self):
        """Update performance metrics."""
        dt = self.clock.get_time() / 1000
        self.cpu_update_accumulator += dt
        
        if self.cpu_update_accumulator >= self.cpu_update_interval:
            self.cpu_usage = cpu_percent(interval=None)
            self.cpu_update_accumulator -= self.cpu_update_interval
            if self.cpu_usage > self.max_cpu_usage:
                self.max_cpu_usage = self.cpu_usage
        
        debug(f"CPU:{self.cpu_usage}%", y=50, x=682)
        debug(f"MAX:{self.max_cpu_usage}%", y=51, x=812)

if __name__ == "__main__":
    game = Game()
    game.run()