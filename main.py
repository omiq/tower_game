import pygame
import heapq
import random

pygame.init()

# Screen and grid settings
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 50  # Size of each cell
ROWS, COLS = HEIGHT // GRID_SIZE, WIDTH // GRID_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Colors
BACKGROUND = (30, 30, 30)
GRID_COLOR = (50, 50, 50)
ENEMY_COLOR = (200, 0, 0)
BASE_COLOR = (0, 200, 0)
PATH_COLOR = (100, 100, 255)
WALL_COLOR = (150, 150, 150)

# Define a simple grid (0 = walkable, 1 = wall)
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

# Set the home base in the center of the grid
base_x, base_y = COLS // 2, ROWS // 2
grid[base_y][base_x] = 2  # Mark the home base position

# Enemy spawn point (top-left corner)
enemy_start = (0, 0)

# A* Pathfinding algorithm
def heuristic(a, b):
    """Manhattan distance heuristic for A*"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def get_neighbors(node, grid):
    """Returns valid neighbors for pathfinding"""
    x, y = node
    neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
    return [(nx, ny) for nx, ny in neighbors if 0 <= nx < COLS and 0 <= ny < ROWS and grid[ny][nx] != 1]

def a_star(start, goal, grid):
    """A* pathfinding algorithm"""
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]  # Return reversed path

        for neighbor in get_neighbors(current, grid):
            temp_g_score = g_score[current] + 1
            if temp_g_score < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return []  # No path found

# Enemy class
class Enemy:
    def __init__(self, enemy_type="basic", game=None):
        # Enemy type configurations
        self.enemy_types = {
            "basic": {
                "speed": 1,
                "health": 100,
                "color": (255, 0, 0),  # Red
                "size": 20
            },
            "fast": {
                "speed": 2,
                "health": 50,
                "color": (0, 255, 0),  # Green
                "size": 15
            },
            "tank": {
                "speed": 0.5,
                "health": 200,
                "color": (128, 128, 128),  # Gray
                "size": 25
            }
        }
        
        # Set properties based on enemy type
        self.type = enemy_type
        self.stats = self.enemy_types[enemy_type]
        self.speed = self.stats["speed"]
        self.health = self.stats["health"]
        self.color = self.stats["color"]
        self.size = self.stats["size"]
        
        # Position and path variables
        self.pos = pygame.Vector2(enemy_start[0] * GRID_SIZE, enemy_start[1] * GRID_SIZE)
        self.path = []
        self.current_path_index = 0
        self.is_dead = False
        self.reached_base = False
        
        # Store game reference
        self.game = game
        
        # Get initial path
        self.calculate_path()

    def calculate_path(self):
        """Recalculates the enemy's path when walls are placed."""
        if self.game:
            start = (int(self.pos.x // GRID_SIZE), int(self.pos.y // GRID_SIZE))
            self.path = a_star(start, (base_x, base_y), self.game.grid.grid)
            self.current_path_index = 0

    def update(self):
        """Move along the path"""
        if self.path and self.current_path_index < len(self.path):
            target_x, target_y = self.path[self.current_path_index]
            target_x *= GRID_SIZE
            target_y *= GRID_SIZE

            dx, dy = target_x - self.pos.x, target_y - self.pos.y
            distance = max(1, (dx ** 2 + dy ** 2) ** 0.5)  # Avoid division by zero
            move_x, move_y = (dx / distance) * self.speed, (dy / distance) * self.speed

            self.pos.x += move_x
            self.pos.y += move_y

            # If close to the next target position, move to the next path point
            if abs(dx) < self.speed and abs(dy) < self.speed:
                self.current_path_index += 1
                
            # Check if reached base
            if self.current_path_index >= len(self.path):
                self.reached_base = True

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, 
                         (int(self.pos.x), int(self.pos.y)), 
                         self.size)
        # Draw health bar
        health_bar_length = 30
        health_ratio = self.health / self.enemy_types[self.type]["health"]
        pygame.draw.rect(screen, (255, 0, 0), 
                        (self.pos.x - health_bar_length/2, 
                         self.pos.y - self.size - 5,
                         health_bar_length, 5))
        pygame.draw.rect(screen, (0, 255, 0),
                        (self.pos.x - health_bar_length/2,
                         self.pos.y - self.size - 5,
                         health_bar_length * health_ratio, 5))

class Wave:
    def __init__(self, enemy_count, enemy_types, spawn_delay):
        self.enemy_count = enemy_count  # Total enemies in this wave
        self.enemy_types = enemy_types  # List of enemy types to spawn
        self.spawn_delay = spawn_delay  # Delay between enemy spawns (milliseconds)
        self.enemies_spawned = 0        # Counter for spawned enemies
        self.last_spawn_time = 0        # Track last spawn time
        self.is_complete = False        # Flag for wave completion

class WaveManager:
    def __init__(self, game):
        self.game = game
        self.current_wave = 0
        self.active_enemies = []
        self.waves = []
        self.current_wave_obj = None
        self.wave_countdown = 3000  # 3 seconds between waves
        self.wave_start_time = 0
        self.setup_waves()

    def setup_waves(self):
        # Example wave configurations
        # Each wave gets progressively harder
        self.waves = [
            Wave(enemy_count=5, enemy_types=['basic'], spawn_delay=1000),
            Wave(enemy_count=8, enemy_types=['basic', 'basic', 'fast'], spawn_delay=800),
            Wave(enemy_count=12, enemy_types=['basic', 'fast', 'tank'], spawn_delay=600),
        ]
        self.current_wave_obj = self.waves[0]

    def update(self, current_time):
        # Between waves countdown
        if self.wave_countdown > 0:
            if self.wave_start_time == 0:
                self.wave_start_time = current_time
            
            elapsed = current_time - self.wave_start_time
            self.wave_countdown = max(3000 - elapsed, 0)
            
            if self.wave_countdown == 0:
                self.start_next_wave()
                return

        if not self.current_wave_obj:
            return

        # Check if it's time to spawn a new enemy
        if (current_time - self.current_wave_obj.last_spawn_time >= self.current_wave_obj.spawn_delay and 
            self.current_wave_obj.enemies_spawned < self.current_wave_obj.enemy_count):
            
            # Spawn new enemy
            enemy_type = random.choice(self.current_wave_obj.enemy_types)
            new_enemy = Enemy(enemy_type, self.game)
            self.active_enemies.append(new_enemy)
            
            self.current_wave_obj.enemies_spawned += 1
            self.current_wave_obj.last_spawn_time = current_time

        # Update all active enemies
        for enemy in self.active_enemies[:]:  # Create copy to safely remove while iterating
            enemy.update()
            if enemy.is_dead or enemy.reached_base:
                self.active_enemies.remove(enemy)

        # Check if wave is complete
        if (self.current_wave_obj.enemies_spawned >= self.current_wave_obj.enemy_count and 
            len(self.active_enemies) == 0):
            self.current_wave_obj.is_complete = True
            self.start_next_wave()

    def start_next_wave(self):
        self.current_wave += 1
        if self.current_wave <= len(self.waves):
            self.current_wave_obj = self.waves[self.current_wave - 1]
            self.wave_countdown = 0
            self.wave_start_time = 0
        else:
            print("Game Complete!")

    def spawn_enemy(self, enemy_type):
        # Create enemy based on type
        return Enemy(enemy_type, self.game)

class Grid:
    def __init__(self):
        self.grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        # Set the home base in the center of the grid
        self.grid[base_y][base_x] = 2  # Mark the home base position

    def draw(self, screen):
        # Draw grid lines
        for x in range(0, WIDTH, GRID_SIZE):
            pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))
        
        # Draw walls and base
        for y in range(ROWS):
            for x in range(COLS):
                if self.grid[y][x] == 1:  # Wall
                    pygame.draw.rect(screen, WALL_COLOR, 
                                   (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
                elif self.grid[y][x] == 2:  # Base
                    pygame.draw.rect(screen, BASE_COLOR, 
                                   (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

    def toggle_wall(self, pos):
        x, y = pos
        if 0 <= x < COLS and 0 <= y < ROWS:
            if self.grid[y][x] == 0:  # Place wall
                self.grid[y][x] = 1
            elif self.grid[y][x] == 1:  # Remove wall
                self.grid[y][x] = 0

    def get_grid_pos(self, mouse_pos):
        x, y = mouse_pos
        return (x // GRID_SIZE, y // GRID_SIZE)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize game components
        self.grid = Grid()
        self.wave_manager = WaveManager(self)  # Pass self to WaveManager
        
        # UI elements
        self.font = pygame.font.Font(None, 36)
        
    def run(self):
        while self.running:
            current_time = pygame.time.get_ticks()
            
            # Handle events
            self.handle_events()
            
            # Update
            self.wave_manager.update(current_time)
            
            # Draw
            self.screen.fill(BACKGROUND)
            
            # Draw grid and walls
            self.grid.draw(self.screen)
            
            # Draw enemies
            for enemy in self.wave_manager.active_enemies:
                enemy.draw(self.screen)
            
            # Draw UI
            self.draw_ui()
            
            pygame.display.flip()
            self.clock.tick(60)

    def draw_ui(self):
        # Draw wave information
        wave_text = f"Wave: {self.wave_manager.current_wave}"
        enemies_text = f"Enemies: {len(self.wave_manager.active_enemies)}"
        
        wave_surface = self.font.render(wave_text, True, (255, 255, 255))
        enemies_surface = self.font.render(enemies_text, True, (255, 255, 255))
        
        self.screen.blit(wave_surface, (10, 10))
        self.screen.blit(enemies_surface, (10, 50))
        
        # If between waves, show countdown
        if self.wave_manager.wave_countdown > 0:
            countdown_text = f"Next wave in: {self.wave_manager.wave_countdown // 1000}"
            countdown_surface = self.font.render(countdown_text, True, (255, 255, 255))
            self.screen.blit(countdown_surface, 
                           (WIDTH//2 - countdown_surface.get_width()//2, 
                            HEIGHT//2))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    grid_pos = self.grid.get_grid_pos(mouse_pos)
                    self.grid.toggle_wall(grid_pos)
                    
                    # Recalculate paths for all enemies when wall placement changes
                    for enemy in self.wave_manager.active_enemies:
                        enemy.calculate_path()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()

pygame.quit()
