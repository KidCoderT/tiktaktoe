import sys
import pygame
import kct_pygame_tools as kpt

WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("tik-tak-toe")

clock = pygame.time.Clock()

background = pygame.Surface((WIDTH, HEIGHT))
background.fill((20, 189, 172))

LINE_HEIGHT = 10

for i in range(1, 3):
    pygame.draw.line(
        background, (13, 161, 146), (200 * i, 0), (200 * i, HEIGHT), LINE_HEIGHT
    )
    pygame.draw.line(
        background, (13, 161, 146), (0, 200 * i), (WIDTH, 200 * i), LINE_HEIGHT
    )


def run():
    while True:
        screen.blit(background, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":
    run()
