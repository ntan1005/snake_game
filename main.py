import pygame
import random
import math
from constants import *
from entities import Snake, Food

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake WENYAD OOP")
        self.clock = pygame.time.Clock()
        
        # Load Resources
        self.load_assets()
        
        # Game State
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.high_score = self.load_highscore()
        self.speed = 10
        self.state = "menu" # menu, game, settings, gameover
        self.paused = False
        self.frame = 0
        self.particles = []
        self.menu_index = 0
        self.food_timer = 0        
        self.spawn_timer = 0       
        self.FOOD_TIMEOUT = 10000  
        self.SPAWN_INTERVAL = 8000 

    def load_assets(self):
        try:
            self.sound_eat = pygame.mixer.Sound("food.mp3")
            self.sound_eat.set_volume(0.7)
            self.sound_die = pygame.mixer.Sound("gameover.mp3")
            self.sound_die.set_volume(0.7)
            pygame.mixer.music.load("nhac_nen.mp3")
            pygame.mixer.music.play(-1)
            self.font_big = pygame.font.SysFont("Arial", 40, bold=True)
            self.font_small = pygame.font.SysFont("Arial", 25)
        except:
            self.font_big = pygame.font.SysFont("Arial", 40)
            self.font_small = pygame.font.SysFont("Arial", 25)
    

    def load_highscore(self):
        try:
            with open("highscore.txt", "r") as f: return int(f.read())
        except: return 0

    def create_particles(self, x, y, color):
        for _ in range(15):
            self.particles.append({
                "pos": [x + 10, y + 10],
                "vel": [random.uniform(-3, 3), random.uniform(-3, 3)],
                "timer": random.randint(10, 20),
                "color": color
            })

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            
            if event.type == pygame.KEYDOWN:
                if self.state == "menu":
                    if event.key == pygame.K_UP: self.menu_index = (self.menu_index - 1) % 3
                    elif event.key == pygame.K_DOWN: self.menu_index = (self.menu_index + 1) % 3
                    elif event.key == pygame.K_RETURN:
                        if self.menu_index == 0: 
                            self.snake.reset()
                            self.score = 0
                            self.speed = 10
                            self.state = "game"
                        elif self.menu_index == 1: self.state = "settings"
                        else: return False
                
                elif self.state == "game":
                    if event.key in [pygame.K_p, pygame.K_ESCAPE]: self.paused = not self.paused
                    if not self.paused:
                        if event.key == pygame.K_UP and self.snake.dy == 0: self.snake.dx, self.snake.dy = 0, -BLOCK
                        elif event.key == pygame.K_DOWN and self.snake.dy == 0: self.snake.dx, self.snake.dy = 0, BLOCK
                        elif event.key == pygame.K_LEFT and self.snake.dx == 0: self.snake.dx, self.snake.dy = -BLOCK, 0
                        elif event.key == pygame.K_RIGHT and self.snake.dx == 0: self.snake.dx, self.snake.dy = BLOCK, 0
                
                elif self.state == "gameover":
                    if event.key == pygame.K_RETURN: self.state = "menu"
        return True

    def update(self):
        self.frame += 1
        dt = self.clock.get_time() # Lấy thời gian trễ giữa 2 khung hình (ms)

        if self.state == "game" and not self.paused:
            # 1. Cập nhật các bộ đếm thời gian
            self.food_timer += dt
            self.spawn_timer += dt

            # 2. Logic: Cứ 8 giây tự động đổi vị trí/loại mồi (Spawn mới)
            if self.spawn_timer >= self.SPAWN_INTERVAL:
                self.food.spawn()
                self.spawn_timer = 0
                self.food_timer = 0 # Reset luôn cả đếm ngược biến mất khi có mồi mới

            # 3. Logic: 10 giây không ăn thì mồi biến mất (Spawn lại chỗ khác)
            if self.food_timer >= self.FOOD_TIMEOUT:
                self.food.spawn()
                self.food_timer = 0
                self.spawn_timer = 0 # Reset luôn đếm 8s để đồng bộ

            # --- Logic di chuyển của rắn (giữ nguyên nhưng cập nhật reset timer khi ăn) ---
            head_next = (self.snake.body[0][0] + self.snake.dx, self.snake.body[0][1] + self.snake.dy)
            
            if head_next == self.food.pos:
                self.apply_food_effect()
                self.snake.move(grow=True)
                self.food.spawn()
                
                # QUAN TRỌNG: Reset các bộ đếm khi rắn ăn mồi thành công
                self.food_timer = 0
                self.spawn_timer = 0
            else:
                self.snake.move(grow=False)

            # Check va chạm
            head = self.snake.body[0]
            if (head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT or head in self.snake.body[1:]):
                self.sound_die.play()
                if self.score > self.high_score:
                    self.high_score = self.score
                    with open("highscore.txt", "w") as f: f.write(str(self.high_score))
                self.state = "gameover"

        # Update hạt hiệu ứng
        for p in self.particles[:]:
            p["pos"][0] += p["vel"][0]
            p["pos"][1] += p["vel"][1]
            p["timer"] -= 1
            if p["timer"] <= 0: self.particles.remove(p)

    def apply_food_effect(self):
        if self.food.type == "normal":
            self.score += 10
            self.sound_eat.play()
            self.create_particles(*self.food.pos, ACCENT)
            if self.score % 50 == 0: self.speed += 1
        elif self.food.type == "gold":
            self.score += 50
            self.speed = min(25, self.speed + 4) # Tăng speed mạnh
            self.sound_eat.play()
            self.create_particles(*self.food.pos, GOLD)
        elif self.food.type == "bomb":
            self.score = max(0, self.score - 20)
            self.speed = max(5, self.speed - 2) # Giảm speed
            for _ in range(2): 
                if len(self.snake.body) > 2: self.snake.body.pop()
            self.create_particles(*self.food.pos, BOMB)

    def draw(self):
        self.screen.fill(BG)
        # Vẽ Grid
        for y in range(0, HEIGHT, 40): pygame.draw.line(self.screen, (30,30,30), (0,y), (WIDTH,y))
        
        if self.state == "menu":
            self.draw_text("SNAKE WENYAD", WIDTH//2 - 140, 50, self.font_big, MAIN)
            options = ["START", "SETTINGS", "QUIT"]
            for i, opt in enumerate(options):
                color = MAIN if i == self.menu_index else GRAY
                self.draw_text(opt, WIDTH//2 - 50, 180 + i*60, self.font_small, color)

        elif self.state == "game":
            self.snake.draw(self.screen, self.frame)
            self.food.draw(self.screen)
            for p in self.particles:
                pygame.draw.circle(self.screen, p["color"], (int(p["pos"][0]), int(p["pos"][1])), 2)
            self.draw_text(f"Score: {self.score}", 10, 10, self.font_small, WHITE)
            if self.paused: self.draw_text("PAUSED", WIDTH//2-50, HEIGHT//2, self.font_big, WHITE)

        elif self.state == "gameover":
            self.draw_text("GAME OVER", WIDTH//2-100, HEIGHT//2-40, self.font_big, ACCENT)
            self.draw_text("Press Enter to Menu", WIDTH//2-100, HEIGHT//2+20, self.font_small, WHITE)

        pygame.display.flip()

    def draw_text(self, text, x, y, font, color):
        img = font.render(text, True, color)
        self.screen.blit(img, (x, y))

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(self.speed)
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()