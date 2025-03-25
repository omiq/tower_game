import pygame

pygame.init()

# Screen settings
WIDTH, HEIGHT = 600, 400
GRID_SIZE = 50  # Grid cell size
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Set window title to Tower Defense
pygame.display.set_caption("Tower Defense")

# Colors
BACKGROUND = (30, 30, 30)
GRID_COLOR = (50, 50, 50)
TOWER_COLOR = (0, 200, 0)
MENU_COLOR = (50, 50, 50)
TEXT_COLOR = (255, 255, 255)

# Font
font = pygame.font.Font(None, 24)

# Tower list (each tower is a pygame.Rect)
towers = [pygame.Rect(100, 150, GRID_SIZE, GRID_SIZE), pygame.Rect(300, 200, GRID_SIZE, GRID_SIZE)]
selected_tower = None  # Stores which tower is selected for dragging
original_pos = None  # Stores the tower's position before dragging
show_menu = False  # Whether to show the context menu
menu_pos = (0, 0)  # Context menu position

def draw_grid():
    """Draws a grid on the screen."""
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))

def draw_menu():
    """Draws a simple context menu when a tower is clicked."""
    menu_width, menu_height = 120, 60
    menu_rect = pygame.Rect(menu_pos[0], menu_pos[1], menu_width, menu_height)
    pygame.draw.rect(screen, MENU_COLOR, menu_rect)
    pygame.draw.rect(screen, (200, 200, 200), menu_rect, 2)  # Border

    # Draw text
    text = font.render("Upgrade", True, TEXT_COLOR)
    screen.blit(text, (menu_pos[0] + 10, menu_pos[1] + 10))
    text = font.render("Sell", True, TEXT_COLOR)
    screen.blit(text, (menu_pos[0] + 10, menu_pos[1] + 35))

def is_valid_placement(tower, ignore_tower=None):
    """Checks if a tower is placed within valid bounds and not overlapping."""
    # Ensure the tower is fully within the screen bounds
    if tower.left < 0 or tower.right > WIDTH or tower.top < 0 or tower.bottom > HEIGHT:
        return False

    # Ensure the tower is not overlapping with other towers (excluding itself)
    for other in towers:
        if other != ignore_tower and tower.colliderect(other):
            return False

    return True

def place_new_tower(mouse_pos):
    """Places a new tower at the nearest grid position if the spot is valid."""
    x = round(mouse_pos[0] / GRID_SIZE) * GRID_SIZE
    y = round(mouse_pos[1] / GRID_SIZE) * GRID_SIZE
    new_tower = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)

    if is_valid_placement(new_tower):  # Check if placement is valid
        towers.append(new_tower)  # Add new tower
    else:
        print("Invalid placement! Tower overlaps another or is out of bounds.")

running = True
dragging = False  # Whether a tower is being dragged
offset_x, offset_y = 0, 0  # Drag offset

while running:
    screen.fill(BACKGROUND)
    draw_grid()  # Draw the grid

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                clicked_tower = None
                for tower in towers:
                    if tower.collidepoint(event.pos):  # Check if clicking a tower
                        clicked_tower = tower
                        offset_x, offset_y = event.pos[0] - tower.x, event.pos[1] - tower.y
                        original_pos = (tower.x, tower.y)  # Store original position before dragging
                        break  # Stop after first match

                if clicked_tower:
                    if show_menu and selected_tower == clicked_tower:
                        # If clicking the same tower, toggle menu off
                        show_menu = False
                    else:
                        selected_tower = clicked_tower
                        show_menu = True
                        menu_pos = (selected_tower.x + GRID_SIZE, selected_tower.y)  # Menu next to tower
                    dragging = True  # Allow dragging
                else:
                    show_menu = False  # Clicked outside, hide menu
            elif event.button == 3:  # Right click to place a new tower
                place_new_tower(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            if dragging and selected_tower:
                # Snap tower to the nearest grid position
                new_x = round(selected_tower.x / GRID_SIZE) * GRID_SIZE
                new_y = round(selected_tower.y / GRID_SIZE) * GRID_SIZE

                # Check if the new position is valid
                temp_rect = pygame.Rect(new_x, new_y, GRID_SIZE, GRID_SIZE)
                if is_valid_placement(temp_rect, ignore_tower=selected_tower):
                    # Apply the snapped position
                    selected_tower.x = new_x
                    selected_tower.y = new_y
                else:
                    # If invalid, return tower to original position
                    selected_tower.x, selected_tower.y = original_pos

            dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if dragging and selected_tower:
                selected_tower.x = event.pos[0] - offset_x
                selected_tower.y = event.pos[1] - offset_y

    # Draw towers
    for tower in towers:
        pygame.draw.rect(screen, TOWER_COLOR, tower)

    # Draw context menu if open
    if show_menu:
        draw_menu()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
