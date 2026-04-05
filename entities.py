import pygame
import random
from constants import *

class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.body = [(100, 100), (80, 100), (60, 100)]
        self.dx, self.dy = BLOCK, 0
        self.color = MAIN

    def move(self, grow=False):
        head = (self.body[0][0] + self.dx, self.body[0][1] + self.dy)
        self.body.insert(0, head)
        if not grow:
            self.body.pop()

    def draw(self, screen, frame):
        for i, (x, y) in enumerate(self.body):
            offset = (frame % 2) * 2
            size = max(8, BLOCK - (i * 0.5))
            color_val = max(100, 255 - i*10)
            color = (0, color_val, 120) if i > 0 else self.color
            
            rect = pygame.Rect(x + (BLOCK-size)/2, y + (BLOCK-size)/2 + offset, size, size)
            pygame.draw.rect(screen, color, rect, border_radius=int(size/3))
            
            if i == 0: # Vẽ mắt cho đầu
                self._draw_eyes(screen, x, y, offset)

    def _draw_eyes(self, screen, x, y, offset):
        if self.dx == BLOCK: eyes = [(x+14,y+5+offset),(x+14,y+14+offset)]
        elif self.dx == -BLOCK: eyes = [(x+6,y+5+offset),(x+6,y+14+offset)]
        elif self.dy == -BLOCK: eyes = [(x+5,y+6+offset),(x+14,y+6+offset)]
        else: eyes = [(x+5,y+14+offset),(x+14,y+14+offset)]
        for ex, ey in eyes:
            pygame.draw.circle(screen, (0,0,0), (ex, ey), 3)

class Food:
    def __init__(self):
        self.spawn()

    def spawn(self):
        self.pos = (random.randrange(0, WIDTH, BLOCK), random.randrange(0, HEIGHT, BLOCK))
        r = random.random()
        if r < 0.2: self.type = "gold"   # 20% mồi vàng
        elif r < 0.4: self.type = "bomb" # 20% mồi đen
        else: self.type = "normal"      # 60% mồi thường

    def draw(self, screen):
        f_center = (self.pos[0] + BLOCK//2, self.pos[1] + BLOCK//2)
        color = ACCENT if self.type == "normal" else GOLD if self.type == "gold" else BOMB
        
        pygame.draw.circle(screen, color, f_center, BLOCK//2)
        if self.type == "bomb": # Vẽ nhân đỏ cho bom
            pygame.draw.circle(screen, (255,0,0), f_center, 4)
        pygame.draw.circle(screen, WHITE, (f_center[0]-3, f_center[1]-3), 3)