import pygame
import heapq

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

def get_neighbors(node):
    """Returns valid neighbors for pathfinding"""
    x, y = node
    neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
    return [(nx, ny) for nx, ny in neighbors if 0 <= nx < COLS and 0 <= ny < ROWS and grid[ny][nx] != 1]

def a_star(start, goal):
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

        for neighbor in get_neighbors(current):
            temp_g_score = g_score[current] + 1
            if temp_g_score < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return []  # No path found

# Enemy class
class Enemy:
    def __init__(self, start, goal):
        self.goal = goal
        self.rect = pygame.Rect(start[0] * GRID_SIZE, start[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        self.speed = 2
        self.recalculate_path()

    def recalculate_path(self):
        """Recalculates the enemy's path when walls are placed."""
        self.path = a_star((self.rect.x // GRID_SIZE, self.rect.y // GRID_SIZE), self.goal)
        self.current_index = 0

    def update(self):
        """Move along the path"""
        if self.path and self.current_index < len(self.path):
            target_x, target_y = self.path[self.current_index]
            target_x *= GRID_SIZE
            target_y *= GRID_SIZE

            dx, dy = target_x - self.rect.x, target_y - self.rect.y
            distance = max(1, (dx ** 2 + dy ** 2) ** 0.5)  # Avoid division by zero
            move_x, move_y = (dx / distance) * self.speed, (dy / distance) * self.speed

            self.rect.x += move_x
            self.rect.y += move_y

            # If close to the next target position, move to the next path point
            if abs(dx) < self.speed and abs(dy) < self.speed:
                self.current_index += 1

# Create an enemy
enemy = Enemy(enemy_start, (base_x, base_y))

running = True
while running:
    screen.fill(BACKGROUND)

    # Draw grid
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))

    # Draw base
    pygame.draw.rect(screen, BASE_COLOR, (base_x * GRID_SIZE, base_y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

    # Draw walls
    for row in range(ROWS):
        for col in range(COLS):
            if grid[row][col] == 1:
                pygame.draw.rect(screen, WALL_COLOR, (col * GRID_SIZE, row * GRID_SIZE, GRID_SIZE, GRID_SIZE))

    # Draw path (for debugging)
    if enemy.path:
        for node in enemy.path:
            pygame.draw.rect(screen, PATH_COLOR, (node[0] * GRID_SIZE, node[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

    # Draw enemy
    pygame.draw.rect(screen, ENEMY_COLOR, enemy.rect)

    # Update enemy movement
    enemy.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:  # Right-click to place/remove walls
                x, y = event.pos[0] // GRID_SIZE, event.pos[1] // GRID_SIZE
                if grid[y][x] == 0:  # Place wall
                    grid[y][x] = 1
                elif grid[y][x] == 1:  # Remove wall
                    grid[y][x] = 0
                enemy.recalculate_path()  # Update enemy path

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
