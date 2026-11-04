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
RED_HP        = (220, 50, 50)
HP_BG         = (60, 20, 20)

# --- Травинки (статичный фон) ---
grass_blades = []
for _ in range(700):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    h = random.randint(4, 14)
    color = random.choice([(35, 130, 45), (55, 170, 65), (25, 100, 35)])
    grass_blades.append((x, y, h, color))

SIZE = 22
player_speed = 3.5
font = pygame.font.SysFont("Arial", 22, bold=True)
big_font = pygame.font.SysFont("Arial", 52, bold=True)


# --- Враг ---
class Enemy:
    def __init__(self, x, y, speed, patrol_range):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.speed = speed
        self.patrol_range = patrol_range
        self.start_x = x
        self.direction = 1
        self.hit_cooldown = 0

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.x > self.start_x + self.patrol_range:
            self.direction = -1
        elif self.rect.x < self.start_x - self.patrol_range:
            self.direction = 1
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

    def draw(self, surface, t):
        cx, cy = self.rect.center
        cy += math.sin(t * 0.008 + cx) * 2
        points = [(cx, cy - 15), (cx + 15, cy), (cx, cy + 15), (cx - 15, cy)]
        pygame.draw.polygon(surface, (120, 30, 30), points)
        pygame.draw.polygon(surface, (60, 10, 10), points, 2)
        pygame.draw.circle(surface, (255, 80, 80), (cx, cy - 5), 4)


def spawn_gem():
    return [random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)]


# --- Отрисовка ---
def draw_emerald(surface, x, y, size, t, facing="down", walk_phase=0.0):
    bob = math.sin(t * 0.004 + walk_phase) * (4 if walk_phase else 2)
    cx, cy = x, y + bob

    offset_x = {"left": 4, "right": -4}.get(facing, 0)
    shadow = pygame.Surface((size * 2, size), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 70), (0, 0, size * 2, size))
    surface.blit(shadow, (cx - size + offset_x, cy + size - 6))

    top    = (cx, cy - size)
    right  = (cx + size * 0.75, cy)
    bottom = (cx, cy + size)
    left   = (cx - size * 0.75, cy)

    pygame.draw.polygon(surface, EMERALD, [top, right, bottom, left])
    pygame.draw.polygon(surface, EMERALD_DARK, [top, right, bottom, left], 2)
    pygame.draw.line(surface, EMERALD_LIGHT, top, bottom, 1)
    pygame.draw.line(surface, EMERALD_LIGHT, left, right, 1)

    shine_offsets = {
        "up":    (-size * 0.25, -size * 0.45),
        "down":  (-size * 0.25, -size * 0.25),
        "left":  (-size * 0.40, -size * 0.30),
        "right": (-size * 0.10, -size * 0.30),
    }
    sx, sy = shine_offsets.get(facing, (-size * 0.25, -size * 0.35))
    pygame.draw.circle(surface, SHINE, (int(cx + sx), int(cy + sy)), 4)
    pygame.draw.circle(surface, (255, 255, 255), (int(cx + sx + 3), int(cy + sy + 2)), 1)


def draw_gem(surface, x, y, t):
    pulse = 8 + math.sin(t * 0.006) * 2
    glow = pygame.Surface((int(pulse * 4), int(pulse * 4)), pygame.SRCALPHA)
    pygame.draw.circle(glow, (*GOLD_GLOW, 60), (int(pulse * 2), int(pulse * 2)), int(pulse * 2))
    surface.blit(glow, (x - pulse * 2, y - pulse * 2))
    pygame.draw.circle(surface, GOLD, (x, y), int(pulse * 0.6))
    pygame.draw.circle(surface, (255, 255, 255), (x - 1, y - 2), 1)


def draw_hp_bar(surface, hp, max_hp):
    """Рисует полоску здоровья в правом верхнем углу."""
    bar_w, bar_h = 160, 20
    x = WIDTH - bar_w - 15
    y = 12
    # фон
    pygame.draw.rect(surface, HP_BG, (x, y, bar_w, bar_h), border_radius=6)
    # заполнение
    fill_w = int(bar_w * hp / max_hp)
    if fill_w > 0:
        pygame.draw.rect(surface, RED_HP, (x, y, fill_w, bar_h), border_radius=6)
    # рамка
    pygame.draw.rect(surface, (255, 255, 255), (x, y, bar_w, bar_h), 2, border_radius=6)
    # текст
    hp_txt = font.render(f"HP {hp}/{max_hp}", True, (255, 255, 255))
    surface.blit(hp_txt, (x + bar_w // 2 - hp_txt.get_width() // 2, y + bar_h + 4))


# --- Сброс игры ---
def reset_game():
    global player_x, player_y, player_facing, player_walk_phase
    global gems, enemies, score, hp, game_over

    player_x, player_y = WIDTH // 2, HEIGHT // 2
    player_facing = "down"
    player_walk_phase = 0.0
    gems = [spawn_gem() for _ in range(6)]
    enemies = [
        Enemy(150, 150, 2.5, 100),
        Enemy(WIDTH - 200, 400, 2.0, 120),
        Enemy(300, HEIGHT - 150, 3.0, 80),
    ]
    score = 0
    hp = 3
    game_over = False


# --- Инициализация ---
reset_game()
MAX_HP = 3

# --- Основной цикл ---
running = True
t = 0
while running:
    dt = clock.tick(60)
    t += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r and game_over:
            reset_game()

    # --- Обновление, только если игра идёт ---
    if not game_over:
        keys = pygame.key.get_pressed()
        moving = False

        if keys[pygame.K_LEFT]  or keys[pygame.K_a]:
            player_x -= player_speed; player_facing = "left";  moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_x += player_speed; player_facing = "right"; moving = True
        if keys[pygame.K_UP]    or keys[pygame.K_w]:
            player_y -= player_speed; player_facing = "up";    moving = True
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]:
            player_y += player_speed; player_facing = "down";  moving = True

        player_walk_phase = player_walk_phase + 0.25 if moving else 0.0

        player_x = max(SIZE, min(WIDTH  - SIZE, player_x))
        player_y = max(SIZE, min(HEIGHT - SIZE, player_y))

        # Сбор кристаллов
        for gem in gems[:]:
            if math.hypot(gem[0] - player_x, gem[1] - player_y) < SIZE + 8:
                gems.remove(gem)
                score += 1
                gems.append(spawn_gem())

        # Враги
        for enemy in enemies:
            enemy.update()

        # Столкновение с врагом → минус жизнь
        player_rect = pygame.Rect(player_x - SIZE, player_y - SIZE, SIZE * 2, SIZE * 2)
        for enemy in enemies:
            if player_rect.colliderect(enemy.rect) and enemy.hit_cooldown == 0:
                dx = player_x - enemy.rect.centerx
                dy = player_y - enemy.rect.centery
                dist = math.hypot(dx, dy) or 1
                player_x += (dx / dist) * 70
                player_y += (dy / dist) * 70
                player_x = max(SIZE, min(WIDTH  - SIZE, player_x))
                player_y = max(SIZE, min(HEIGHT - SIZE, player_y))

                hp -= 1
                enemy.hit_cooldown = 40  # ~0.6 сек

                if hp <= 0:
                    hp = 0
                    game_over = True

    # --- Отрисовка ---
    screen.fill(GRASS_DARK)
    for x, y, h, c in grass_blades:
        pygame.draw.line(screen, c, (x, y), (x - 2, y - h), 1)

    for gem in gems:
        draw_gem(screen, gem[0], gem[1], t)

    for enemy in enemies:
        enemy.draw(screen, t)

    draw_emerald(screen, player_x, player_y, SIZE, t, player_facing, player_walk_phase)

    # UI
    screen.blit(font.render(f"Собрано: {score}", True, (255, 255, 255)), (12, 10))
    draw_hp_bar(screen, hp, MAX_HP)
    screen.blit(font.render("WASD / стрелки — движение", True, (220, 255, 220)),
                (12, HEIGHT - 30))

    # --- Game Over ---
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        go_txt = big_font.render("GAME OVER", True, (255, 90, 90))
        screen.blit(go_txt, (WIDTH // 2 - go_txt.get_width() // 2, HEIGHT // 2 - 80))

        sc_txt = font.render(f"Кристаллов собрано: {score}", True, (255, 255, 255))
        screen.blit(sc_txt, (WIDTH // 2 - sc_txt.get_width() // 2, HEIGHT // 2 - 10))

        rs_txt = font.render("Нажмите R, чтобы начать заново", True, (230, 230, 230))
        screen.blit(rs_txt, (WIDTH // 2 - rs_txt.get_width() // 2, HEIGHT // 2 + 40))

    pygame.display.flip()

pygame.quit()
