"""
Игру разработал Сливный Дмитрий Игоревич, для аттестации на 2 год преподавания в Яндекс Лицее

"""



import pygame
import random
import math
from pygame import mixer

pygame.init()
mixer.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Astro Miner")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

font_small = pygame.font.SysFont('arial', 18)
font_medium = pygame.font.SysFont('arial', 24)
font_large = pygame.font.SysFont('arial', 36)




# Загрузка изображений
"""
Со спрайтами есть проблемма пока не могу точно понять где я ошибся, проблемма в том что при загрузке изображений, все равботает,
но не отображаются выстрелы. поэтому следующий код можно раскомментировать иди закоментировать. Так как если изображения не загружаются, 
то в этом случает отрисовываются обычные геометрические фигуры
"""


def load_image(name, scale=1):
    """
    Первый комент будут отрисованы фигры, второй со спрайтами
    """
    img = pygame.image.load(f"Картинок не будет").convert_alpha()
    #img = pygame.image.load(f"assets/images/{name}.png").convert_alpha()
    width = img.get_width()
    height = img.get_height()
    return pygame.transform.scale(img, (int(width * scale), int(height * scale)))

try:
    player_img = load_image("player_ship", 0.5)

    asteroid_imgs = [
        load_image("asteroid1", 0.4),
        load_image("asteroid2", 0.4),
        load_image("asteroid3", 0.4)
    ]

    enemy_img = load_image("enemy_ship", 0.4)

    bullet_img = load_image("bullet", 0.3)

    resource_imgs = [
        load_image("resource1", 0.3),
        load_image("resource2", 0.3),
        load_image("resource3", 0.3)
    ]

    background_img = load_image("space_bg")
    background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

    station_img = load_image("space_station", 0.6)

except FileNotFoundError as e:
    print(f"Ошибка загрузки изображений: {e}")

    # Заглушки если изображения не найдены
    player_img = pygame.Surface((50, 30), pygame.SRCALPHA)
    pygame.draw.polygon(player_img, GREEN, [(0, 15), (50, 0), (50, 30)])

    asteroid_imgs = [pygame.Surface((40, 40), pygame.SRCALPHA) for _ in range(3)]
    for img in asteroid_imgs:
        pygame.draw.circle(img, (150, 150, 150), (20, 20), 20)

    enemy_img = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.polygon(enemy_img, RED, [(20, 0), (40, 40), (0, 40)])

    bullet_img = pygame.Surface((10, 5), pygame.SRCALPHA)
    pygame.draw.rect(bullet_img, YELLOW, (0, 0, 10, 5))

    resource_imgs = [pygame.Surface((20, 20), pygame.SRCALPHA) for _ in range(3)]
    colors = [BLUE, YELLOW, GREEN]
    for i, img in enumerate(resource_imgs):
        pygame.draw.circle(img, colors[i], (10, 10), 10)

    background_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background_img.fill(BLACK)
    for _ in range(100):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        pygame.draw.circle(background_img, WHITE, (x, y), 1)

    station_img = pygame.Surface((80, 80), pygame.SRCALPHA)
    pygame.draw.circle(station_img, (100, 100, 255), (40, 40), 40)
    pygame.draw.rect(station_img, (100, 100, 255), (30, 20, 20, 40))

# Загрузка звуков
try:
    shoot_sound = mixer.Sound(buffer=bytearray(100))
    explosion_sound = mixer.Sound(buffer=bytearray(100))
    collect_sound = mixer.Sound(buffer=bytearray(100))
    engine_sound = mixer.Sound(buffer=bytearray(100))
    engine_sound.set_volume(0.3)

    # Фоновая музыка
    mixer.music.load("assets/sounds/background.wav")
    mixer.music.set_volume(0.5)
    mixer.music.play(-1)
except:
    print("Звуки не найдены.")
    


# Класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.original_image = player_img
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.centery = SCREEN_HEIGHT // 2
        self.speed = 5
        self.angle = 0
        self.health = 100
        self.max_health = 100
        self.resources = 0
        self.resources_collected = 0
        self.score = 0
        self.upgrades = {
            "engine": {"level": 1, "cost": 50, "value": 5},
            "weapon": {"level": 1, "cost": 50, "value": 1},
            "shield": {"level": 1, "cost": 50, "value": 100}
        }
        self.last_shot = 0
        self.shot_delay = 250 
        self.engine_particles = []
        self.invincible = False
        self.invincible_time = 0

    def update(self):
        dx, dy = 0, 0

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle += 5
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle -= 5

        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            angle_rad = math.radians(self.angle)
            dx = self.speed * math.cos(angle_rad)
            dy = -self.speed * math.sin(angle_rad)

            if random.random() < 0.3:
                angle_rad = math.radians(self.angle + 180)
                offset_x = math.cos(angle_rad) * 30
                offset_y = -math.sin(angle_rad) * 30
                self.engine_particles.append({
                    "x": self.rect.centerx + offset_x,
                    "y": self.rect.centery + offset_y,
                    "size": random.randint(3, 8),
                    "life": 20
                })

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            angle_rad = math.radians(self.angle)
            dx = -self.speed * 0.5 * math.cos(angle_rad)
            dy = self.speed * 0.5 * math.sin(angle_rad)

        self.rect.x += dx
        self.rect.y += dy

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

        for particle in self.engine_particles[:]:
            particle["life"] -= 1
            if particle["life"] <= 0:
                self.engine_particles.remove(particle)

        # Неуязвимость после получения урона
        if self.invincible:
            if pygame.time.get_ticks() - self.invincible_time > 2000:  
                self.invincible = False

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shot_delay:
            self.last_shot = now
            shoot_sound.play()

            bullets = []
            angle_rad = math.radians(self.angle)

            for i in range(self.upgrades["weapon"]["value"]):
                offset = (i - (self.upgrades["weapon"]["value"] - 1) / 2) * 15
                offset_x = math.cos(angle_rad + math.pi / 2) * offset
                offset_y = -math.sin(angle_rad + math.pi / 2) * offset

                bullet = Bullet(
                    self.rect.centerx + math.cos(angle_rad) * 30 + offset_x,
                    self.rect.centery - math.sin(angle_rad) * 30 + offset_y,
                    self.angle
                )
                bullets.append(bullet)

            return bullets
        return []

    def take_damage(self, amount):
        if not self.invincible:
            self.health -= amount
            self.invincible = True
            self.invincible_time = pygame.time.get_ticks()
            explosion_sound.play()
            if self.health <= 0:
                self.health = 0
                return True 
        return False

    def draw_health_bar(self, surface):
        bar_width = 50
        bar_height = 10
        fill = (self.health / self.max_health) * bar_width
        outline_rect = pygame.Rect(self.rect.x, self.rect.y - 15, bar_width, bar_height)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y - 15, fill, bar_height)
        pygame.draw.rect(surface, RED, fill_rect)
        pygame.draw.rect(surface, WHITE, outline_rect, 2)

    def draw_engine_particles(self, surface):
        for particle in self.engine_particles:
            pygame.draw.circle(
                surface,
                YELLOW,
                (int(particle["x"]), int(particle["y"])),
                particle["size"]
            )


# Класс астероида
class Asteroid(pygame.sprite.Sprite):
    def __init__(self, x=None, y=None, size=None):
        super().__init__()
        self.size = size if size else random.choice([1, 1, 1, 2, 2, 3])  
        self.image = asteroid_imgs[self.size - 1]
        self.original_image = self.image

        if x and y:
            self.rect = self.image.get_rect(center=(x, y))
        else:
            # Появление с краев экрана
            side = random.randint(0, 3)
            if side == 0: 
                self.rect = self.image.get_rect(
                    center=(random.randint(0, SCREEN_WIDTH), -50))
            elif side == 1: 
                self.rect = self.image.get_rect(
                    center=(SCREEN_WIDTH + 50, random.randint(0, SCREEN_HEIGHT)))
            elif side == 2: 
                self.rect = self.image.get_rect(
                    center=(random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + 50))
            else: 
                self.rect = self.image.get_rect(
                    center=(-50, random.randint(0, SCREEN_HEIGHT)))

            self.health = self.size * 20
            self.max_health = self.health
            self.damage = self.size * 10
            self.resources = self.size * 5
            self.speed = random.uniform(1, 3 - self.size * 0.5)

            angle = random.uniform(0, math.pi * 2)
            self.dx = math.cos(angle) * self.speed
            self.dy = -math.sin(angle) * self.speed

            self.rotation = 0
            self.rotation_speed = random.uniform(-2, 2)

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

        self.rotation = (self.rotation + self.rotation_speed) % 360
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        self.rect = self.image.get_rect(center=self.rect.center)

        if (self.rect.right < -100 or self.rect.left > SCREEN_WIDTH + 100 or
                self.rect.bottom < -100 or self.rect.top > SCREEN_HEIGHT + 100):
            self.kill()

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            explosion_sound.play()
            return True 
        return False

    def draw_health_bar(self, surface):
        if self.health < self.max_health:
            bar_width = 30 * self.size
            bar_height = 5
            fill = (self.health / self.max_health) * bar_width
            outline_rect = pygame.Rect(
                self.rect.centerx - bar_width // 2,
                self.rect.y - 10,
                bar_width,
                bar_height
            )
            fill_rect = pygame.Rect(
                self.rect.centerx - bar_width // 2,
                self.rect.y - 10,
                fill,
                bar_height
            )
            pygame.draw.rect(surface, RED, fill_rect)
            pygame.draw.rect(surface, WHITE, outline_rect, 1)


# Класс ресурсов
class Resource(pygame.sprite.Sprite):
    def __init__(self, x, y, resource_type=None):
        super().__init__()
        self.type = resource_type if resource_type else random.randint(0, 2)
        self.image = resource_imgs[self.type]
        self.rect = self.image.get_rect(center=(x, y))
        self.value = (self.type + 1) * 5
        self.rotation = 0
        self.rotation_speed = random.uniform(-1, 1)

    def update(self):
        self.rotation = (self.rotation + self.rotation_speed) % 360
        self.image = pygame.transform.rotate(resource_imgs[self.type], self.rotation)
        self.rect = self.image.get_rect(center=self.rect.center)


# Класс пули
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.original_image = bullet_img
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = angle
        self.speed = 10
        angle_rad = math.radians(self.angle)
        self.dx = math.cos(angle_rad) * self.speed
        self.dy = -math.sin(angle_rad) * self.speed
        self.damage = 10

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

        if (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or
                self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT):
            self.kill()


# Класс врага
class Enemy(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.image = enemy_img
        self.original_image = enemy_img
        self.rect = self.image.get_rect()

        # Появление с краев экрана
        side = random.randint(0, 3)
        if side == 0: 
            self.rect.centerx = random.randint(0, SCREEN_WIDTH)
            self.rect.centery = -50
        elif side == 1: 
            self.rect.centerx = SCREEN_WIDTH + 50
            self.rect.centery = random.randint(0, SCREEN_HEIGHT)
        elif side == 2: 
            self.rect.centerx = random.randint(0, SCREEN_WIDTH)
            self.rect.centery = SCREEN_HEIGHT + 50
        else:  
            self.rect.centerx = -50
            self.rect.centery = random.randint(0, SCREEN_HEIGHT)

        self.speed = random.uniform(1, 3)
        self.health = 50
        self.max_health = 50
        self.damage = 15
        self.player = player
        self.last_shot = 0
        self.shot_delay = 1500 

    def update(self):
        # Движение к игроку
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        if dist != 0:
            dx = dx / dist * self.speed
            dy = dy / dist * self.speed
            self.rect.x += dx
            self.rect.y += dy

        # Поворот к игроку
        angle = math.degrees(math.atan2(-dy, dx)) - 90
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shot_delay:
            self.last_shot = now
            shoot_sound.play()

            dx = self.player.rect.centerx - self.rect.centerx
            dy = self.player.rect.centery - self.rect.centery
            angle = math.degrees(math.atan2(-dy, dx)) - 90

            bullet = Bullet(self.rect.centerx, self.rect.centery, angle)
            bullet.damage = self.damage
            bullet.image.fill(RED)

            return bullet
        return None

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            explosion_sound.play()
            return True
        return False

    def draw_health_bar(self, surface):
        bar_width = 40
        bar_height = 5
        fill = (self.health / self.max_health) * bar_width
        outline_rect = pygame.Rect(
            self.rect.centerx - bar_width // 2,
            self.rect.y - 10,
            bar_width,
            bar_height
        )
        fill_rect = pygame.Rect(
            self.rect.centerx - bar_width // 2,
            self.rect.y - 10,
            fill,
            bar_height
        )
        pygame.draw.rect(surface, RED, fill_rect)
        pygame.draw.rect(surface, WHITE, outline_rect, 1)


# Класс космической станции
class SpaceStation(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = station_img
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 4
        self.rect.centery = SCREEN_HEIGHT // 4
        self.radius = 60 
        self.rotation = 0
        self.rotation_speed = 0.2

    def update(self):
        self.rotation = (self.rotation + self.rotation_speed) % 360
        self.image = pygame.transform.rotate(station_img, self.rotation)
        self.rect = self.image.get_rect(center=(self.rect.centerx, self.rect.centery))

    def can_dock(self, player):
        distance = math.hypot(
            self.rect.centerx - player.rect.centerx,
            self.rect.centery - player.rect.centery
        )
        return distance < self.radius


# Класс взрыва
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.size = size
        self.images = []

        # Создание анимации взрыва
        for i in range(8):
            img = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            alpha = 255 - i * 32
            if alpha < 0:
                alpha = 0
            pygame.draw.circle(
                img,
                (255, 165 + i * 10, 0, alpha),
                (size, size),
                size - i * (size // 8)
            )
            self.images.append(img)

        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.counter = 0

    def update(self):
        explosion_speed = 4
        self.counter += 1

        if self.counter >= explosion_speed:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.index]
                self.rect = self.image.get_rect(center=self.rect.center)


# Класс игры
class Game:
    def __init__(self):
        self.player = Player()
        self.all_sprites = pygame.sprite.Group(self.player)
        self.asteroids = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.resources = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.station = SpaceStation()
        self.all_sprites.add(self.station)

        self.level = 1
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 10000  
        self.asteroid_spawn_timer = 0
        self.asteroid_spawn_delay = 3000 
        self.game_over = False
        self.docked = False
        self.show_upgrade_menu = False
        self.clock = pygame.time.Clock()
        self.running = True

        for _ in range(5):
            self.spawn_asteroid()

    def spawn_asteroid(self):
        asteroid = Asteroid()
        self.asteroids.add(asteroid)
        self.all_sprites.add(asteroid)

    def spawn_enemy(self):
        enemy = Enemy(self.player)
        self.enemies.add(enemy)
        self.all_sprites.add(enemy)

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                if event.key == pygame.K_SPACE:
                    # Выстрел игрока
                    bullets = self.player.shoot()
                    for bullet in bullets:
                        self.bullets.add(bullet)
                        self.all_sprites.add(bullet)

                if event.key == pygame.K_e and self.station.can_dock(self.player):
                    # Стыковка со станцией
                    if not self.docked:
                        self.docked = True
                        self.show_upgrade_menu = True
                    else:
                        self.docked = False
                        self.show_upgrade_menu = False
                        self.player.resources = 0 

                if event.key == pygame.K_r and self.game_over:
                    self.__init__()

    def update(self):
        if not self.game_over:
            self.all_sprites.update()

            # Проверка столкновений пуль игрока с астероидами
            for bullet in self.bullets:
                hits = pygame.sprite.spritecollide(bullet, self.asteroids, False)
                for asteroid in hits:
                    if asteroid.take_damage(bullet.damage):
                        # Создание ресурсов при уничтожении астероида
                        for _ in range(asteroid.resources // 5):
                            resource = Resource(
                                asteroid.rect.centerx,
                                asteroid.rect.centery,
                                random.randint(0, 2)
                            )
                            self.resources.add(resource)
                            self.all_sprites.add(resource)

                        # Создание взрыва
                        explosion = Explosion(
                            asteroid.rect.centerx,
                            asteroid.rect.centery,
                            asteroid.size * 10
                        )
                        self.explosions.add(explosion)
                        self.all_sprites.add(explosion)

                        self.player.score += asteroid.size * 10
                        asteroid.kill()
                    bullet.kill()

            # Проверка столкновений пуль игрока с врагами
            for bullet in self.bullets:
                hits = pygame.sprite.spritecollide(bullet, self.enemies, False)
                for enemy in hits:
                    if enemy.take_damage(bullet.damage):
                        # Создание ресурсов при уничтожении врага
                        for _ in range(3):
                            resource = Resource(
                                enemy.rect.centerx,
                                enemy.rect.centery,
                                random.randint(0, 2)
                            )
                            self.resources.add(resource)
                            self.all_sprites.add(resource)

                        # Создание взрыва
                        explosion = Explosion(
                            enemy.rect.centerx,
                            enemy.rect.centery,
                            40
                        )
                        self.explosions.add(explosion)
                        self.all_sprites.add(explosion)

                        self.player.score += 50
                        enemy.kill()
                    bullet.kill()

            # Проверка столкновений игрока с ресурсами
            hits = pygame.sprite.spritecollide(self.player, self.resources, True)
            for resource in hits:
                collect_sound.play()
                self.player.resources += resource.value
                self.player.resources_collected += resource.value

            # Проверка столкновений игрока с астероидами
            hits = pygame.sprite.spritecollide(self.player, self.asteroids, False)
            for asteroid in hits:
                if self.player.take_damage(asteroid.damage):

                    explosion = Explosion(
                        self.player.rect.centerx,
                        self.player.rect.centery,
                        60
                    )
                    self.explosions.add(explosion)
                    self.all_sprites.add(explosion)

                    self.game_over = True

            # Проверка столкновений игрока с врагами
            hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
            for enemy in hits:
                if self.player.take_damage(enemy.damage):

                    explosion = Explosion(
                        self.player.rect.centerx,
                        self.player.rect.centery,
                        60
                    )
                    self.explosions.add(explosion)
                    self.all_sprites.add(explosion)

                    self.game_over = True

            # Выстрелы врагов
            for enemy in self.enemies:
                bullet = enemy.shoot()
                if bullet:
                    self.bullets.add(bullet)
                    self.all_sprites.add(bullet)

            # Проверка столкновений пуль врагов с игроком
            for bullet in self.bullets:
                if bullet.rect.colliderect(self.player.rect):
                    if self.player.take_damage(bullet.damage):
                        # Создание большого взрыва при смерти игрока
                        explosion = Explosion(
                            self.player.rect.centerx,
                            self.player.rect.centery,
                            60
                        )
                        self.explosions.add(explosion)
                        self.all_sprites.add(explosion)

                        self.game_over = True
                    bullet.kill()

            # Спавн новых астероидов
            now = pygame.time.get_ticks()
            if now - self.asteroid_spawn_timer > self.asteroid_spawn_delay:
                self.asteroid_spawn_timer = now
                self.spawn_asteroid()

                if random.random() < 0.3:
                    self.spawn_asteroid()

            # Спавн новых врагов
            if now - self.enemy_spawn_timer > self.enemy_spawn_delay:
                self.enemy_spawn_timer = now
                self.spawn_enemy()

                # Увеличиваем сложность с уровнем
                if random.random() < 0.2 * self.level:
                    self.spawn_enemy()

                # Уменьшаем задержку спавна
                self.enemy_spawn_delay = max(3000, self.enemy_spawn_delay - 500)

                self.level += 1

    def draw(self):
        screen.blit(background_img, (0, 0))

        for sprite in self.all_sprites:
            screen.blit(sprite.image, sprite.rect)

            if isinstance(sprite, Player):
                sprite.draw_health_bar(screen)
                sprite.draw_engine_particles(screen)
            elif isinstance(sprite, Asteroid):
                sprite.draw_health_bar(screen)
            elif isinstance(sprite, Enemy):
                sprite.draw_health_bar(screen)

        for resource in self.resources:
            screen.blit(resource.image, resource.rect)

        for explosion in self.explosions:
            screen.blit(explosion.image, explosion.rect)
        
        self.draw_hud()

        if self.show_upgrade_menu:
            self.draw_upgrade_menu()

        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def draw_hud(self):
        pygame.draw.rect(screen, (0, 0, 0, 150), (0, 0, SCREEN_WIDTH, 40))

        health_text = font_medium.render(f"Здоровье: {self.player.health}/{self.player.max_health}", True, WHITE)
        screen.blit(health_text, (10, 10))

        resources_text = font_medium.render(f"Ресурсы: {self.player.resources}", True, YELLOW)
        screen.blit(resources_text, (300, 40))

        score_text = font_medium.render(f"Очки: {self.player.score}", True, WHITE)
        screen.blit(score_text, (500, 40))

        level_text = font_medium.render(f"Уровень: {self.level}", True, WHITE)
        screen.blit(level_text, (700, 40))

        hints_text = font_small.render("WASD: Перемещение | SPACE: Выстрел | E: Меню станции | ESC: Выход", True, WHITE)
        screen.blit(hints_text, (SCREEN_WIDTH - hints_text.get_width() - 10, 10))

        if self.station.can_dock(self.player) and not self.docked:
            dock_text = font_medium.render("Нажмите E, что бы зайти в меню станции", True, GREEN)
            screen.blit(dock_text, (SCREEN_WIDTH // 2 - dock_text.get_width() // 2, 50))

    def draw_upgrade_menu(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        menu_rect = pygame.Rect(
            SCREEN_WIDTH // 4,
            SCREEN_HEIGHT // 4,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2
        )
        pygame.draw.rect(screen, (30, 30, 50), menu_rect)
        pygame.draw.rect(screen, WHITE, menu_rect, 2)

        title_text = font_large.render("Улучшения", True, WHITE)
        screen.blit(title_text, (
            SCREEN_WIDTH // 2 - title_text.get_width() // 2,
            SCREEN_HEIGHT // 4 + 20
        ))

        resources_text = font_medium.render(f"Необходимо ресурсов: {self.player.resources}", True, YELLOW)
        screen.blit(resources_text, (
            SCREEN_WIDTH // 2 - resources_text.get_width() // 2,
            SCREEN_HEIGHT // 4 + 70
        ))

        # Кнопки улучшений
        self.draw_upgrade_button("Двигатель", self.player.upgrades["engine"], SCREEN_HEIGHT // 4 + 120)
        self.draw_upgrade_button("Оружие", self.player.upgrades["weapon"], SCREEN_HEIGHT // 4 + 170)
        self.draw_upgrade_button("Защита", self.player.upgrades["shield"], SCREEN_HEIGHT // 4 + 220)

        # Кнопка выхода
        exit_text = font_medium.render("Нажмите Е для выхода", True, WHITE)
        screen.blit(exit_text, (
            SCREEN_WIDTH // 2 - exit_text.get_width() // 2,
            SCREEN_HEIGHT // 4 + 280
        ))

    def draw_upgrade_button(self, name, upgrade, y_pos):
        button_rect = pygame.Rect(
            SCREEN_WIDTH // 4 + 50,
            y_pos,
            SCREEN_WIDTH // 2 - 100,
            40
        )

        if self.player.resources >= upgrade["cost"]:
            color = (0, 100, 0)
            hover_color = (0, 150, 0)
            text_color = WHITE
        else:
            color = (100, 0, 0)
            hover_color = (100, 0, 0)
            text_color = (150, 150, 150)

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        if button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, hover_color, button_rect)

            if mouse_click[0] and self.player.resources >= upgrade["cost"]:
                self.player.resources -= upgrade["cost"]
                upgrade["level"] += 1
                upgrade["cost"] = upgrade["level"] * 50

                if name.lower() == "engine":
                    self.player.speed = 5 + upgrade["level"]
                elif name.lower() == "weapon":
                    self.player.upgrades["weapon"]["value"] = 1 + upgrade["level"] // 2
                elif name.lower() == "shield":
                    self.player.max_health = 100 + upgrade["level"] * 20
                    self.player.health = self.player.max_health

                collect_sound.play()
        else:
            pygame.draw.rect(screen, color, button_rect)

        pygame.draw.rect(screen, WHITE, button_rect, 1)


        button_text = font_medium.render(
            f"{name} (Уровень {upgrade['level']}) - Цена: {upgrade['cost']}",
            True,
            text_color
        )
        screen.blit(button_text, (
            button_rect.x + 10,
            button_rect.y + button_rect.height // 2 - button_text.get_height() // 2
        ))

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        game_over_text = font_large.render("Конец игры!", True, RED)
        screen.blit(game_over_text, (
            SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
            SCREEN_HEIGHT // 2 - 100
        ))

        # Статистика
        stats_text = [
            f"Очки: {self.player.score}",
            f"Ресурсов собрано: {self.player.resources_collected}",
            f"Уровень: {self.level}",
            f"Врагов уничтожено: {self.player.score // 50}",
            f"Астеройдов уничтожено: {self.player.resources_collected // 5}"
        ]

        for i, text in enumerate(stats_text):
            stat_line = font_medium.render(text, True, WHITE)
            screen.blit(stat_line, (
                SCREEN_WIDTH // 2 - stat_line.get_width() // 2,
                SCREEN_HEIGHT // 2 - 30 + i * 30
            ))

        # Подсказка
        restart_text = font_medium.render("Нажмите R для рестарта или ESC для выхода", True, WHITE)
        screen.blit(restart_text, (
            SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
            SCREEN_HEIGHT // 2 + 150
        ))

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.process_events()
            self.update()
            self.draw()


# Запуск игры
if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()