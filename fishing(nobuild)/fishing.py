import pygame
import random


class FishingMiniGame:
    def __init__(self, fish_obj):
        self.fish = fish_obj
        # Настройки шкалы
        self.bar_h = 400
        self.bar_y = 150
        self.slider_h = 28

        # случайная позиция зеленого
        max_pos = int(self.bar_h - self.fish.size)
        self.fish_y = random.randint(0, max_pos)

        self.fish_vel = 0

        fish_center = self.fish_y + (self.fish.size / 2)
        self.slider_y = fish_center - (self.slider_h / 2)

        self.slider_y = max(0, min(self.slider_y, self.bar_h - self.slider_h))
        self.slider_vel = 0

        self.progress = 10.0  # с 10%
        self.game_over = False
        self.ticks = 0

    def update(self):
        if self.game_over:
            return

        self.ticks += 1

        # 1. зелёный + сложность рыбы
        random_jerk = random.uniform(-0.3, 0.3) * self.fish.difficulty
        self.fish_vel += random_jerk

        max_speed = 1.5 + (self.fish.difficulty * 0.5)
        self.fish_vel = max(-max_speed, min(max_speed, self.fish_vel))

        self.fish_vel *= 0.95 # трение
        self.fish_y += self.fish_vel

        if self.fish_y < 0 or self.fish_y > self.bar_h - self.fish.size:
            self.fish_vel *= -0.5  # отскок
            self.fish_y = max(0, min(self.fish_y, self.bar_h - self.fish.size))

        # 2. желтый - игрок
        is_pressed = pygame.mouse.get_pressed()[0]
        if is_pressed:
            self.slider_vel -= 0.4
        else:
            self.slider_vel += 0.3

        self.slider_vel *= 0.9
        self.slider_y += self.slider_vel

        if self.slider_y < 0: self.slider_y = 0; self.slider_vel = 0
        if self.slider_y > self.bar_h - self.slider_h:
            self.slider_y = self.bar_h - self.slider_h
            self.slider_vel = 0

        # коллизии
        collision = (self.slider_y <= self.fish_y + self.fish.size) and \
                    (self.slider_y + self.slider_h >= self.fish_y)

        if collision:
            catch_speed = 0.3 / (1 + (self.fish.difficulty * 0.1))
            self.progress += catch_speed
        else:
            if self.ticks > 60:
                fail_penalty = 0.15 * (1 + (self.fish.difficulty * 0.05))
                self.progress -= fail_penalty

        self.progress = max(0, min(100, self.progress))

        if self.ticks > 60 and self.progress <= 0:
            self.game_over = True

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 0, 0), (90, self.bar_y - 10, 60, self.bar_h + 20))
        pygame.draw.rect(screen, (40, 40, 50), (94, self.bar_y - 6, 52, self.bar_h + 12))

        # зеленый
        fish_rect = pygame.Rect(98, self.bar_y + self.fish_y, 44, self.fish.size)
        pygame.draw.rect(screen, (0, 80, 0), fish_rect.inflate(4, 4))
        pygame.draw.rect(screen, (50, 255, 50), fish_rect)

        # желтый
        slider_rect = pygame.Rect(94, self.bar_y + self.slider_y, 52, self.slider_h)
        pygame.draw.rect(screen, (255, 255, 255), slider_rect, 4)
        pygame.draw.rect(screen, (255, 200, 0), slider_rect.inflate(-4, -4))

        # синий
        prog_bg = pygame.Rect(160, self.bar_y, 24, self.bar_h)
        pygame.draw.rect(screen, (0, 0, 0), prog_bg.inflate(4, 4))
        pygame.draw.rect(screen, (30, 30, 40), prog_bg)

        progress_h = (self.progress / 100) * self.bar_h
        if progress_h > 0:
            prog_fill = pygame.Rect(160, self.bar_y + (self.bar_h - progress_h), 24, progress_h)
            pygame.draw.rect(screen, (0, 120, 255), prog_fill)