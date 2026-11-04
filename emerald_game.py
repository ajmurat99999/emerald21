import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Изумруд гуляет по траве")
clock = pygame.time.Clock()

# --- Цвета ---
GRASS_DARK  = (30, 120, 40)
GRASS_LIGHT = (45, 160, 55)
EMERALD       = (16, 185, 129)
EMERALD_LIGHT = (90, 235, 175)
EMERALD_DARK  = (5, 100, 70)
SHINE         = (215, 255, 235)
GOLD          = (255, 215, 0)
GOLD_GLOW     = (255, 245, 160)

# --- Травинки (статичный фон) ---
grass_blades = []
for _ in range(700):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    h = random.randint(4, 14)
    color = random.choice([(35, 130, 45), (55, 170, 65), (25, 100, 35)])
    grass_blades.append((x, y, h, color))

# --- Игрок ---
player_x, player_y = WIDTH // 2, HEIGHT // 2
player_speed = 3.5
SIZE = 22

# --- Кристаллы ---
def spawn_gem():
    return [random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)]

gems = [spawn_gem() for _ in range(6)]
score = 0

font = pygame.font.SysFont("Arial", 22, bold=True)


def draw_emerald(surface, x, y, size, t):
    """Рисует изумруд в виде огранённого камня с покачиванием."""
    bob = math.sin(t * 0.004) * 3
    cx, cy = x, y + bob

    # тень
    shadow = pygame.Surface((size * 2, size), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 70), (0, 0, size * 2, size))
    surface.blit(shadow, (cx - size, cy + size - 6))

    # вершины ромба
    top    = (cx, cy - size)
    right  = (cx + size * 0.75, cy)
    bottom = (cx, cy + size)
    left   = (cx - size * 0.75, cy)

    pygame.draw.polygon(surface, EMERALD, [top, right, bottom, left])
    pygame.draw.polygon(surface, EMERALD_DARK, [top, right, bottom, left], 2)

    # грани (блики)
    pygame.draw.line(surface, EMERALD_LIGHT, top, bottom, 1)
    pygame.draw.line(surface, EMERALD_LIGHT, left, right, 1)

    # блик
    pygame.draw.circle(surface, SHINE, (int(cx - size * 0.25), int(cy - size * 0.35)), 4)


def draw_gem(surface, x, y, t):
    """Золотой кристалл с лёгким свечением."""
    pulse = 8 + math.sin(t * 0.006) * 2
    glow = pygame.Surface((int(pulse * 4), int(pulse * 4)), pygame.SRCALPHA)
    pygame.draw.circle(glow, (*GOLD_GLOW, 60), (int(pulse * 2), int(pulse * 2)), int(pulse * 2))
    surface.blit(glow, (x - pulse * 2, y - pulse * 2))
    pygame.draw.circle(surface, GOLD, (x, y), int(pulse * 0.6))
    pygame.draw.circle(surface, (255, 255, 255), (x - 1, y - 2), 1)


running = True
t = 0
while running:
    dt = clock.tick(60)
    t += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Управление ---
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]  or keys[pygame.K_a]: player_x -= player_speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]: player_x += player_speed
    if keys[pygame.K_UP]    or keys[pygame.K_w]: player_y -= player_speed
    if keys[pygame.K_DOWN]  or keys[pygame.K_s]: player_y += player_speed

    # границы
    player_x = max(SIZE, min(WIDTH  - SIZE, player_x))
    player_y = max(SIZE, min(HEIGHT - SIZE, player_y))

    # --- Отрисовка фона ---
    screen.fill(GRASS_DARK)
    # лёгкие пятна травы
    for x, y, h, c in grass_blades:
        pygame.draw.line(screen, c, (x, y), (x - 2, y - h), 1)

    # --- Кристаллы ---
    for gem in gems:
        draw_gem(screen, gem[0], gem[1], t)

    # --- Столкновения ---
    for gem in gems[:]:
        if math.hypot(gem[0] - player_x, gem[1] - player_y) < SIZE + 8:
            gems.remove(gem)
            score += 1
            gems.append(spawn_gem())

    # --- Игрок ---
    draw_emerald(screen, player_x, player_y, SIZE, t)

    # --- Счёт ---
    score_txt = font.render(f"Собрано: {score}", True, (255, 255, 255))
    screen.blit(score_txt, (12, 10))

    hint = font.render("WASD / стрелки — движение", True, (220, 255, 220))
    screen.blit(hint, (12, HEIGHT - 30))

    pygame.display.flip()

pygame.quit()
