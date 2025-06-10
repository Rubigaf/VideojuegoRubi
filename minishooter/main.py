import pygame 
import random

# Inicializar pygame
pygame.init()

# Configuración de pantalla
WIDTH, HEIGHT = 1080, 720
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini Shooter")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Cargar fondo
background = pygame.image.load("imagenes/fondo_espacio.png").convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Control de frames por segundo
FPS = 60

# ---------- Clase del Jugador ----------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = pygame.image.load("imagenes/shuttle.png").convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (60, 50))
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed = 5
        self.lives = 5
        self.invulnerable = False
        self.invulnerable_timer = 0

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

        if self.invulnerable:
            self.invulnerable_timer -= 1
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
                self.image.set_alpha(255)
            else:
                self.image.set_alpha(128 if self.invulnerable_timer % 10 < 5 else 255)

# ---------- Clase Bala ----------
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -7

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

# ---------- Clase Enemigo ----------
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = pygame.image.load("imagenes/asteroiderealjaja.png").convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.randint(2, 5)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.y = random.randint(-100, -40)
            self.rect.x = random.randint(0, WIDTH - self.rect.width)

# ---------- Clase PowerUp ----------
class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = pygame.image.load("imagenes/estrella_poweup.png").convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (40, 40))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-150, -50)
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

# Grupos
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
powerups = pygame.sprite.Group()

# Crear jugador
player = Player()
all_sprites.add(player)

# Enemigos iniciales
for _ in range(5):
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

# Variables
clock = pygame.time.Clock()
running = True
score = 0
game_over = False
powerup_timer = 0

# Bucle principal
try:
    while running:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    bullet = Bullet(player.rect.centerx, player.rect.top)
                    all_sprites.add(bullet)
                    bullets.add(bullet)
                elif event.key == pygame.K_r and game_over:
                    game_over = False
                    score = 0
                    player.lives = 5
                    player.rect.centerx = WIDTH // 2
                    player.invulnerable = False
                    all_sprites = pygame.sprite.Group()
                    bullets = pygame.sprite.Group()
                    enemies = pygame.sprite.Group()
                    powerups = pygame.sprite.Group()
                    all_sprites.add(player)
                    for _ in range(5):
                        enemy = Enemy()
                        all_sprites.add(enemy)
                        enemies.add(enemy)

        if not game_over:
            player.update(keys)
            bullets.update()
            enemies.update()
            powerups.update()

            hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
            for hit in hits:
                score += 10
                if len(enemies) < 5:
                    enemy = Enemy()
                    all_sprites.add(enemy)
                    enemies.add(enemy)

            if not player.invulnerable:
                hits = pygame.sprite.spritecollide(player, enemies, True)
                if hits:
                    player.lives -= 1
                    if player.lives <= 0:
                        game_over = True
                    else:
                        player.invulnerable = True
                        player.invulnerable_timer = 60
                        for hit in hits:
                            enemy = Enemy()
                            all_sprites.add(enemy)
                            enemies.add(enemy)

            collected = pygame.sprite.spritecollide(player, powerups, True)
            for _ in collected:
                if player.lives < 5:
                    player.lives += 1

            powerup_timer += 1
            if powerup_timer >= FPS * 5:
                powerup = PowerUp()
                all_sprites.add(powerup)
                powerups.add(powerup)
                powerup_timer = 0

        # Dibujar fondo
        WIN.blit(background, (0, 0))
        all_sprites.draw(WIN)

        font = pygame.font.Font(None, 36)
        lives_text = font.render(f'Lives: {player.lives}', True, WHITE)
        score_text = font.render(f'Score: {score}', True, WHITE)
        WIN.blit(lives_text, (10, 10))
        WIN.blit(score_text, (10, 50))

        if game_over:
            game_over_text = font.render('GAME OVER - Press R to Restart', True, WHITE)
            text_rect = game_over_text.get_rect(center=(WIDTH / 2, HEIGHT / 2))
            WIN.blit(game_over_text, text_rect)

        pygame.display.flip()

except Exception as e:
    print("Ocurrió un error:", e)

finally:
    pygame.quit()
