import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 400, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

clock = pygame.time.Clock()
FPS = 60

# Colors
SKY_BLUE = (135, 206, 235)
PIPE_GREEN = (34, 139, 34)
GROUND_BROWN = (139, 69, 19)
BIRD_YELLOW = (255, 223, 0)

# Fonts
big_font = pygame.font.SysFont("Arial", 48, bold=True)
small_font = pygame.font.SysFont("Arial", 28)

# Game variables
bird_x = 100
bird_y = 250
bird_vel = 0
GRAVITY = 0.58
FLAP_STRENGTH = -11.5
BIRD_RADIUS = 18

PIPE_WIDTH = 72
PIPE_GAP = 175
PIPE_SPEED = 3.2

pipes = []
score = 0
game_active = False
game_over_state = False

def reset_game():
    global bird_y, bird_vel, pipes, score, game_active, game_over_state
    bird_y = 250
    bird_vel = 0
    pipes = [{"x": WIDTH + 50, "height": random.randint(140, 420), "passed": False}]
    score = 0
    game_active = False
    game_over_state = False

def draw_bird():
    # Body
    pygame.draw.circle(screen, BIRD_YELLOW, (int(bird_x), int(bird_y)), BIRD_RADIUS)
    # Eye
    pygame.draw.circle(screen, (255, 255, 255), (int(bird_x + 10), int(bird_y - 6)), 7)
    pygame.draw.circle(screen, (0, 0, 0), (int(bird_x + 12), int(bird_y - 6)), 3)
    # Beak
    pygame.draw.polygon(screen, (255, 140, 0), [
        (bird_x + 16, bird_y + 2),
        (bird_x + 28, bird_y),
        (bird_x + 16, bird_y - 4)
    ])

def create_pipe():
    height = random.randint(130, HEIGHT - PIPE_GAP - 180)
    return {"x": WIDTH + 30, "height": height, "passed": False}

def main():
    global bird_vel, bird_y, score, game_active, game_over_state

    reset_game()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                if event.type == pygame.KEYDOWN and event.key != pygame.K_SPACE:
                    continue

                if not game_active and not game_over_state:
                    game_active = True
                    # Add initial pipe if needed
                    if not pipes:
                        pipes.append(create_pipe())
                elif game_over_state:
                    reset_game()
                    game_active = True
                else:
                    bird_vel = FLAP_STRENGTH

        # === UPDATE LOGIC ===
        if game_active and not game_over_state:
            # Bird physics
            bird_vel += GRAVITY
            bird_y += bird_vel

            # Move pipes
            for pipe in pipes:
                pipe["x"] -= PIPE_SPEED

            # Add new pipe
            if len(pipes) == 0 or pipes[-1]["x"] < WIDTH - 210:
                pipes.append(create_pipe())

            # Remove off-screen pipes
            if pipes and pipes[0]["x"] < -PIPE_WIDTH - 10:
                pipes.pop(0)

            # Scoring
            for pipe in pipes:
                if not pipe["passed"] and pipe["x"] + PIPE_WIDTH < bird_x:
                    pipe["passed"] = True
                    score += 1

            # Collisions
            # Ceiling & Ground
            if bird_y - BIRD_RADIUS < 0 or bird_y + BIRD_RADIUS > HEIGHT - 85:
                game_over_state = True
                game_active = False

            # Pipe collisions
            for pipe in pipes:
                px = pipe["x"]
                pheight = pipe["height"]
                if (bird_x + BIRD_RADIUS > px and bird_x - BIRD_RADIUS < px + PIPE_WIDTH):
                    if (bird_y - BIRD_RADIUS < pheight) or (bird_y + BIRD_RADIUS > pheight + PIPE_GAP):
                        game_over_state = True
                        game_active = False

        # === DRAWING ===
        screen.fill(SKY_BLUE)

        # Draw pipes
        for pipe in pipes:
            # Top pipe
            pygame.draw.rect(screen, PIPE_GREEN, (pipe["x"], 0, PIPE_WIDTH, pipe["height"]))
            # Top pipe cap
            pygame.draw.rect(screen, (20, 100, 20), (pipe["x"] - 4, pipe["height"] - 25, PIPE_WIDTH + 8, 30))

            # Bottom pipe
            bottom_start = pipe["height"] + PIPE_GAP
            pygame.draw.rect(screen, PIPE_GREEN, (pipe["x"], bottom_start, PIPE_WIDTH, HEIGHT - bottom_start - 85))
            # Bottom cap
            pygame.draw.rect(screen, (20, 100, 20), (pipe["x"] - 4, bottom_start, PIPE_WIDTH + 8, 30))

        # Draw bird
        draw_bird()

        # Ground
        pygame.draw.rect(screen, GROUND_BROWN, (0, HEIGHT - 85, WIDTH, 85))
        pygame.draw.rect(screen, (34, 139, 34), (0, HEIGHT - 85, WIDTH, 20))  # grass layer

        # Score
        score_text = big_font.render(str(score), True, (255, 255, 255))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 70))

        # Start screen
        if not game_active and not game_over_state:
            title = big_font.render("FLAPPY BIRD", True, (255, 220, 0))
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 180))
            instr = small_font.render("Click or Space to Flap", True, (255, 255, 255))
            screen.blit(instr, (WIDTH//2 - instr.get_width()//2, 320))

        # Game Over
        if game_over_state:
            go = big_font.render("GAME OVER", True, (200, 30, 30))
            screen.blit(go, (WIDTH//2 - go.get_width()//2, 200))
            final = small_font.render(f"Score: {score}", True, (255, 255, 255))
            screen.blit(final, (WIDTH//2 - final.get_width()//2, 270))
            restart = small_font.render("Click to Restart", True, (255, 255, 255))
            screen.blit(restart, (WIDTH//2 - restart.get_width()//2, 340))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()