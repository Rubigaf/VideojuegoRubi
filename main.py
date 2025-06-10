import pygame  # Importa la biblioteca pygame para gráficos y sonido
import random  # Importa random para generar posiciones y velocidades aleatorias

pygame.init()  # Inicializa todos los módulos de pygame (gráficos, eventos, etc.)
pygame.mixer.init()  # Inicializa el módulo de sonido de pygame para música y efectos

# Define el tamaño de la ventana del juego
WIDTH, HEIGHT = 1080, 720  
WIN = pygame.display.set_mode((WIDTH, HEIGHT))  # Crea la ventana del juego con el tamaño definido

pygame.display.set_caption("Mini Shooter")  # Establece el título de la ventana

# Define colores comunes que usaremos (en formato RGB)
WHITE = (255, 255, 255)  # Blanco
BLACK = (0, 0, 0)        # Negro

# Carga la imagen de fondo desde archivo y la ajusta al tamaño de la ventana
background = pygame.image.load("imagenes/fondo_espacio.png").convert()  
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

FPS = 60  # Define los cuadros por segundo para controlar la velocidad del juego

# Carga la música de fondo, ajusta el volumen y la reproduce en bucle
pygame.mixer.music.load("mixkit-tech-house-vibes-130.mp3")  
pygame.mixer.music.set_volume(0.5)  # Volumen entre 0.0 y 1.0
pygame.mixer.music.play(-1)  # Reproduce la música indefinidamente

# Clase que representa al jugador (nave espacial)
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()  # Inicializa la clase base Sprite
        self.original_image = pygame.image.load("imagenes/shuttle.png").convert_alpha()  
        self.image = pygame.transform.scale(self.original_image, (60, 50))  # Escala la imagen
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2  # Centrado horizontal
        self.rect.bottom = HEIGHT - 10  # Posición vertical cerca de abajo
        self.speed = 5  # Velocidad de movimiento
        self.lives = 5  # Vidas iniciales
        self.invulnerable = False  # Invulnerabilidad tras daño
        self.invulnerable_timer = 0  # Tiempo que dura la invulnerabilidad

    def update(self, keys):
        # Movimiento con flechas izquierda/derecha
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        # Limitar dentro de la ventana
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

        # Invulnerabilidad con parpadeo
        if self.invulnerable:
            self.invulnerable_timer -= 1
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
                self.image.set_alpha(255)  # Opacidad normal
            else:
                # Parpadeo: alternar transparencia para efecto flash
                self.image.set_alpha(128 if (self.invulnerable_timer // 5) % 2 == 0 else 255)
        else:
            self.image.set_alpha(255)  # Asegura opacidad normal si no es invulnerable

# Clase para las balas disparadas por el jugador
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -7  # Se mueve hacia arriba

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

# Clase para enemigos (asteroides)
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

# Clase para power-ups que otorgan vidas extra
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

# Grupos para organizar sprites
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
powerups = pygame.sprite.Group()

# Crear jugador y enemigos iniciales
player = Player()
all_sprites.add(player)

for _ in range(5):
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

clock = pygame.time.Clock()
running = True
score = 0
game_over = False
powerup_timer = 0
paused = False  # Variable para pausar el juego

while running:
    clock.tick(FPS)  # Controla FPS

    # Captura eventos (teclado, mouse, cerrar ventana)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            # Disparar bala con espacio si no está en pausa o game over
            if event.key == pygame.K_SPACE and not game_over and not paused:
                bullet = Bullet(player.rect.centerx, player.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)

            # Reiniciar el juego con R si está en game over
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

            # Pausar o reanudar el juego con la tecla P
            elif event.key == pygame.K_p:
                paused = not paused  # Alterna el estado de pausa

    # Si el juego está pausado, no actualizar lógica ni dibujar sprites
    if not paused and not game_over:
        keys = pygame.key.get_pressed()
        player.update(keys)
        bullets.update()
        enemies.update()
        powerups.update()

        # Colisiones entre balas y enemigos
        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for hit in hits:
            score += 10
            # Reemplaza enemigo destruido
            new_enemy = Enemy()
            all_sprites.add(new_enemy)
            enemies.add(new_enemy)

        # Colisiones entre jugador y enemigos
        if not player.invulnerable:
            enemy_hits = pygame.sprite.spritecollide(player, enemies, False)
            if enemy_hits:
                player.lives -= 1
                player.invulnerable = True
                player.invulnerable_timer = FPS * 2  # 2 segundos invulnerable
                # Se mantiene el parpadeo en Player.update con set_alpha()

        # Colisiones entre jugador y power-ups
        powerup_hits = pygame.sprite.spritecollide(player, powerups, True)
        for powerup in powerup_hits:
            if player.lives < 5:
                player.lives += 1

        # Generar power-ups cada 10 segundos
        powerup_timer += 1
        if powerup_timer >= FPS * 10:
            powerup = PowerUp()
            all_sprites.add(powerup)
            powerups.add(powerup)
            powerup_timer = 0

        # Terminar juego si vidas llegan a 0
        if player.lives <= 0:
            game_over = True

    # --- DIBUJADO ---
    WIN.blit(background, (0, 0))  # Fondo

    # Si está pausado, muestra mensaje de pausa y no dibuja sprites en movimiento
    if paused:
        font_pause = pygame.font.SysFont("Arial", 80)
        pause_text = font_pause.render("PAUSADO", True, WHITE)
        WIN.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 40))
    else:
        all_sprites.draw(WIN)  # Dibuja todos los sprites normalmente

    # Mostrar puntaje y vidas
    font = pygame.font.SysFont("Arial", 30)
    score_text = font.render(f"Puntaje: {score}", True, WHITE)
    lives_text = font.render(f"Vidas: {player.lives}", True, WHITE)
    WIN.blit(score_text, (10, 10))
    WIN.blit(lives_text, (10, 50))

    # Mensaje de fin de juego
    if game_over:
        game_over_font = pygame.font.SysFont("Arial", 80)
        game_over_text = game_over_font.render("GAME OVER", True, WHITE)
        restart_text = font.render("Presiona R para reiniciar", True, WHITE)
        WIN.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 60))
        WIN.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 30))

    pygame.display.update()  # Actualiza la pantalla

pygame.quit()  # Sale de pygame cuando se cierra la ventana
