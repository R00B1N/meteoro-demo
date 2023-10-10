import pygame
import random
import sys
import math
import os


# pygame setup
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
pygame.display.set_caption("METEORO - DEMO")
running = True


# Lista para almacenar las partículas
particles = []

# Colores
white = (255, 255, 255)
black = (0, 0, 0)

# Definición de los estados
MENU = 0
PLAYING = 1

# Variable para almacenar el estado actual
current_state = MENU

# Cargar música
# Reemplaza con el nombre de tu archivo de música
music_path = os.path.join("assets", "music1.wav")
pygame.mixer.music.load(music_path)
pygame.mixer.music.set_volume(0.5)  # Ajusta el volumen (0.0 a 1.0)
pygame.mixer.music.play(-1)  # -1 para reproducir en bucle


# Clase para representar la nave del jugador
class Player:
    def __init__(self):
        self.image = pygame.image.load(os.path.join("assets", "nave.png"))
        self.image = pygame.transform.scale(
            self.image, (50, 70))  # Escalar la imagen
        self.rect = self.image.get_rect()
        self.rect.center = (400, 500)
        self.speed = 5
        self.direction = 0
        self.score = 0  # Variable para almacenar el puntaje
        self.speed_increment = 0  # Variable para el incremento de velocidad

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed + self.speed_increment
        if keys[pygame.K_RIGHT] and self.rect.right < 800:
            self.rect.x += self.speed + self.speed_increment

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def increase_score(self, points):
        self.score += points
        # Comprobar si se alcanzó un múltiplo de 100 en el puntaje
        if self.score % 100 == 0:
            self.speed_increment += 10  # Aumentar la velocidad al alcanzar un múltiplo de 100


# Clase para representar una partícula
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = random.randint(2, 5)
        self.color = (random.randint(0, 255), random.randint(
            0, 255), random.randint(0, 255))
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-0.5, 0.5)
        self.alpha = 255

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.alpha -= 2
        if self.alpha < 0:
            self.alpha = 0


class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load(os.path.join("assets", "torpedo.png"))
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = 10

    def update(self):
        self.rect.y -= self.speed


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = [pygame.image.load(os.path.join("assets", "explosion1.png")),
                       pygame.image.load(os.path.join(
                           "assets", "explosion2.png")),
                       pygame.image.load(os.path.join(
                           "assets", "explosion3.png")),
                       pygame.image.load(os.path.join("assets", "explosion4.png"))]

        # Escalar las imágenes de explosión
        self.images = [pygame.transform.scale(
            img, (40, 40)) for img in self.images]

        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.frame_change_interval = 75  # Cambiar de frame cada 75 milisegundos
        self.last_update = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_change_interval:
            self.last_update = now
            self.index += 1
            if self.index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.index]
                self.rect = self.image.get_rect()
                self.rect.center = self.images[0].get_rect().center


# Clase para representar un obstáculo utilizando sprite
class ObstacleSprite(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Lista de nombres de archivos de obstáculos
        obstacle_images = ["obstacle1.png", "obstacle2.png", "obstacle3.png"]

        # Elegir aleatoriamente un nombre de archivo de obstáculo
        chosen_obstacle = random.choice(obstacle_images)

        # Cargar la imagen del obstáculo elegido
        self.image = pygame.image.load(os.path.join("assets", chosen_obstacle))
        self.image = pygame.transform.scale(
            self.image, (60, 60))  # Escalar la imagen
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, 800 - self.rect.width)
        self.rect.y = random.randint(-1000, -50)
        self.speed = 3

    def update(self):
        self.rect.y += self.speed


# Función para mostrar la pantalla de juego
def play_game():
    # Cargar imagen de fondo
    background = pygame.image.load(os.path.join("assets", "background.png"))
    background = pygame.transform.scale(
        background, (860, 1024))  # Escalar la imagen
    background_y = 0  # Posición inicial en Y del fondo

    # Variables para el score
    score = 0
    # Intervalo de tiempo (segundos) para incrementar el score
    score_increment_interval = 0.5
    time_since_last_increment = 0.0

    # Crear grupo de sprites para los misiles
    missiles = pygame.sprite.Group()

    # Crear grupo de sprites para las explosiones
    explosions = pygame.sprite.Group()

    # Crear jugador
    player = Player()

    # Crear grupos de sprites
    all_sprites = pygame.sprite.Group()
    obstacles_sprites = pygame.sprite.Group()

    # Tiempo transcurrido en segundos
    elapsed_time = 0

    # Ciclo del juego
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # Espacio para disparar
                    missile = Missile(player.rect.centerx, player.rect.top)
                    all_sprites.add(missile)
                    missiles.add(missile)

        # Limpiar la pantalla
        screen.fill((0, 0, 0))

        # Incrementar el tiempo transcurrido
        elapsed_time += 1 / 60  # Asumiendo 60 FPS

        # Mover al jugador
        player.move()

        # Verificar colisiones entre misiles y obstáculos
        missile_obstacle_collisions = pygame.sprite.groupcollide(
            missiles, obstacles_sprites, True, True)
        for obstacle_sprite in missile_obstacle_collisions.values():
            # Incrementar el puntaje por cada obstáculo eliminado
            score += len(obstacle_sprite)
            for obstacle in obstacle_sprite:
                explosion = Explosion(
                    obstacle.rect.centerx, obstacle.rect.centery)
                all_sprites.add(explosion)
                explosions.add(explosion)

        # Actualizar y dibujar explosiones
        explosions.update()
        explosions.draw(screen)

        # Cambiar aleatoriamente la velocidad y dirección cuando el puntaje es igual o mayor a 100
        if score >= 20:
            for obstacle_sprite in obstacles_sprites:
                if random.random() < 0.01:
                    player.speed += 0.009

        # Mover el fondo (efecto de desplazamiento)
        background_y = (
            background_y + player.speed) % background.get_rect().height
        screen.blit(background, (0, background_y -
                    background.get_rect().height))
        screen.blit(background, (0, background_y))

        # Generar nuevos obstáculos
        if random.randint(1, 50) == 1:
            obstacle_sprite = ObstacleSprite()
            all_sprites.add(obstacle_sprite)
            obstacles_sprites.add(obstacle_sprite)

        # Dibujar al jugador
        player.draw(screen)

        # Actualizar los sprites
        all_sprites.update()

        # Verificar colisiones con obstáculos
        collisions = pygame.sprite.spritecollide(
            player, obstacles_sprites, False)
        if collisions:
            print("¡Has perdido!")
            show_message(f"¡Has perdido! - Tu Puntaje: {score}")
            return  # Salir de la función si el jugador pierde

        # Dibujar los sprites
        all_sprites.draw(screen)

        # Actualizar el tiempo transcurrido y verificar si es tiempo de incrementar el score
        time_since_last_increment += clock.get_time() / 1000  # Convertir a segundos
        if time_since_last_increment >= score_increment_interval:
            # Incrementar el score
            score += 1
            time_since_last_increment = 0.0  # Reiniciar el contador

        # Mostrar la puntuación en la esquina superior derecha
        font = pygame.font.Font(None, 36)
        score_text = font.render("Puntuación: {}".format(score), True, white)
        score_rect = score_text.get_rect()
        score_rect.topright = (800 - 10, 10)  # Esquina superior derecha
        screen.blit(score_text, score_rect)

        pygame.display.flip()
        # Limpiar la pantalla
        screen.fill((0, 0, 0))
        clock.tick(60)


# Función para mostrar un mensaje en pantalla
def show_message(message):
    font = pygame.font.Font(None, 36)
    text = font.render(message, True, white)
    text_rect = text.get_rect(center=(800 // 2, 600 // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    # Mostrar el mensaje durante 2 segundos antes de continuar
    pygame.time.wait(5000)


# Clase para representar un botón
class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text

    def draw(self, surface):
        pygame.draw.rect(surface, white, self.rect)
        font = pygame.font.Font(None, 36)
        text = font.render(self.text, True, black)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)


# Función para mostrar el menú
def show_menu():
    particles = []
    font = pygame.font.Font(None, 72)
    title_text = font.render("Meteoro", True, white)
    title_rect = title_text.get_rect(
        center=(800 // 2, 600 // 4))

    play_button = Button(800 // 2 - 100, 600 // 2, 200, 50, "Jugar")
    levels_button = Button(800 // 2 - 100, 600 // 2 + 100, 200, 50, "Niveles")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if play_button.rect.collidepoint(event.pos):
                        print("¡Has presionado Jugar!")
                        play_game()
                    elif levels_button.rect.collidepoint(event.pos):
                        print("¡Has presionado Niveles!")

        # Generar nuevas partículas aleatorias
        if len(particles) < 100:  # Limitar la cantidad de partículas
            x = random.randint(0, 800)
            y = random.randint(0, 600)
            particles.append(Particle(x, y))

        # Actualizar las partículas
        for particle in particles:
            particle.update()

        # Eliminar partículas que han desaparecido
        particles = [particle for particle in particles if particle.alpha > 0]

        # Limpiar la pantalla
        screen.fill((0, 0, 0))

        # Dibujar las partículas
        for particle in particles:
            pygame.draw.circle(screen, (particle.color[0], particle.color[1], particle.color[2], particle.alpha),
                               (int(particle.x), int(particle.y)), particle.radius)

        # Dibujar el menú sobre las partículas
        screen.blit(title_text, title_rect)
        play_button.draw(screen)
        levels_button.draw(screen)

        clock.tick(60)
        pygame.display.flip()


show_menu()
