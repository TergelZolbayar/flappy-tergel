import pygame
import sys
import random
import os

WIN_WIDTH, WIN_HEIGHT = 600, 800
FPS = 60
GRAVITY = 0.25
JUMP_VELOCITY = -5
PIPE_GAP = 120
PIPE_DIST = 200
SCROLL_SPEED = 2

ASSET_DIR = "assets"

pygame.init()
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird • Python")


def load_image(file_name):
    path = os.path.join(ASSET_DIR, file_name)
    if not os.path.exists(path):
        print(f"Error: Image file '{path}' not found. Please ensure all assets are in the 'assets' directory.")
        pygame.quit()
        sys.exit()
    try:
        img = pygame.image.load(path)
        print(f"Loaded {file_name}: {img.get_width()}x{img.get_height()}")
        return img
    except pygame.error as e:
        print(f"Error loading {file_name}: {e}")
        pygame.quit()
        sys.exit()

try:
    BG = load_image("bg.png").convert()
    BASE = load_image("base.png").convert_alpha()
    BIRD = load_image("bird.png").convert_alpha()
    PIPE = load_image("pipe.png").convert_alpha()
except pygame.error as e:
    print(f"Error loading images: {e}")
    pygame.quit()
    sys.exit()


BG = pygame.transform.scale(BG, (WIN_WIDTH, WIN_HEIGHT))
print(f"Background size after scaling: {BG.get_width()}x{BG.get_height()}")


BASE_HEIGHT = 70 
BASE = pygame.transform.scale(BASE, (WIN_WIDTH, BASE_HEIGHT))
print(f"Base image size after scaling: {BASE.get_width()}x{BASE.get_height()}")


BIRD_WIDTH, BIRD_HEIGHT = 34, 24
BIRD = pygame.transform.scale(BIRD, (BIRD_WIDTH, BIRD_HEIGHT))
print(f"Bird image size after scaling: {BIRD.get_width()}x{BIRD.get_height()}")


PIPE_WIDTH, PIPE_HEIGHT = 80, 400 
PIPE = pygame.transform.scale(PIPE, (PIPE_WIDTH, PIPE_HEIGHT))
print(f"Pipe image size after scaling: {PIPE.get_width()}x{PIPE.get_height()}")

CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont("arial", 32, bold=True)

class Bird:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = 40
        self.y = WIN_HEIGHT // 2
        self.vel = 0
        self.rect = BIRD.get_rect(center=(self.x, self.y))
        self.angle = 0
        self.current_sprite = BIRD
        print(f"Bird reset: position ({self.x}, {self.y}), velocity {self.vel}")

    def update(self):
        self.vel += GRAVITY
        self.y += self.vel
        self.rect.centery = self.y
        self.angle = max(-90, min(25, -self.vel * 8))
        self.current_sprite = pygame.transform.rotate(BIRD, self.angle)
        return self.out_of_bounds()

    def jump(self):
        self.vel = JUMP_VELOCITY
        print("Bird jumped!") 
    def draw(self, surf):
        surf.blit(self.current_sprite, self.current_sprite.get_rect(center=self.rect.center))
        print("Drawing bird")  
    def out_of_bounds(self):
        return self.y >= WIN_HEIGHT - BASE.get_height() or self.y < 0

class PipePair:
    def __init__(self, x):
        self.x = x
        self.reset()

    def reset(self):
        min_height = 50
        max_height = WIN_HEIGHT - BASE.get_height() - PIPE_GAP - min_height
        if max_height <= min_height:
            max_height = min_height + 1
            print(f"Warning: max_height adjusted to {max_height} to prevent invalid range.")
        height = random.randrange(min_height, max_height)
        self.top_rect = PIPE.get_rect(midbottom=(self.x, height))
        self.bottom_rect = PIPE.get_rect(midtop=(self.x, height + PIPE_GAP))
        self.passed = False

    def update(self):
        self.x -= SCROLL_SPEED
        self.top_rect.centerx = self.bottom_rect.centerx = self.x

    def draw(self, surf):
        top_img = pygame.transform.flip(PIPE, False, True)
        surf.blit(top_img, self.top_rect.topleft)
        surf.blit(PIPE, self.bottom_rect.topleft)
        print("Drawing pipes")  

    def collide(self, bird):
        return bird.rect.colliderect(self.top_rect) or bird.rect.colliderect(self.bottom_rect)

    def off_screen(self):
        return self.x < -PIPE.get_width()

def draw_base(surf, base_x):
    surf.blit(BASE, (base_x, WIN_HEIGHT - BASE.get_height()))
    surf.blit(BASE, (base_x + BASE.get_width(), WIN_HEIGHT - BASE.get_height()))
    print("Drawing base")  
def draw_window(surf, bird, pipes, base_x, score):
    surf.blit(BG, (0, 0)) 
    print("Drawing background")
    for p in pipes:
        p.draw(surf) 
    draw_base(surf, base_x)  
    bird.draw(surf)  
    score_txt = FONT.render(str(score), True, (255, 255, 255))
    surf.blit(score_txt, score_txt.get_rect(center=(WIN_WIDTH // 2, 50)))  
    print("Drawing score")
    pygame.display.update()

def game_over_screen(score):
    WIN.blit(BG, (0, 0))  
    game_over_text = FONT.render(f"Game Over! Score: {score}", True, (255, 255, 255))
    restart_text = FONT.render("Press R to Restart", True, (255, 255, 255))
    WIN.blit(game_over_text, game_over_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 - 30)))
    WIN.blit(restart_text, restart_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + 30)))
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
    return False

def main():
    while True:
        bird = Bird()
        pipes = [PipePair(WIN_WIDTH + 100)]
        base_x = 0
        score = 0
        running = True

        
        bird.jump() 

        while running:
            CLOCK.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        bird.jump()
                    if event.key == pygame.K_r:  
                        bird.jump()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    bird.jump()

            if bird.update():
                running = False

            for pipe in pipes:
                pipe.update()
                if pipe.collide(bird):
                    running = False
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    score += 1
                    pipes.append(PipePair(pipes[-1].x + PIPE_DIST))

            pipes = [p for p in pipes if not p.off_screen()]

            base_x -= SCROLL_SPEED
            if base_x <= -BASE.get_width():
                base_x = 0

            draw_window(WIN, bird, pipes, base_x, score)

        if not game_over_screen(score):
            break

    pygame.quit()
    print(f"Final score: {score}")

if __name__ == "__main__":
    main()