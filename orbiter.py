import pygame
import sys


SCREEN_WIDTH, SCREEN_HEIGHT = (800, 600)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Orbiter")

# the coords for the object to orbit around
center = pygame.math.Vector2(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)

# the orbiter's coords
orbiter = pygame.math.Vector2(200, 200)

# the orbiter's speed
speed = 200

# the orbiter's basis
right = pygame.math.Vector2(1, 0)
up = pygame.math.Vector2(0, 1)

# delta time
clock = pygame.time.Clock()
delta = 0

# mainloop
while True:

    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # follow the cursor when the left mouse button is clicked
    if pygame.mouse.get_pressed()[0]:
        x_c, y_c = pygame.mouse.get_pos()
        center = pygame.math.Vector2(x_c, y_c)

    # move a little bit in the x
    move = speed * delta * right
    orbiter += move

    # point the up vector to the center
    up = (center - orbiter).normalize()

    # recalculate our right vector
    right = pygame.math.Vector2(-up.y, up.x)

    # draw the center and the orbiter
    pygame.draw.circle(screen, (255, 0, 0), center, 10)
    pygame.draw.circle(screen, (0, 255, 0), orbiter, 10)

    # draw the basis for visualing
    pygame.draw.line(screen, (255, 0, 0), orbiter, orbiter + 20*right)
    pygame.draw.line(screen, (0, 0, 255), orbiter, orbiter + 20*up)

    # update the screen
    pygame.display.update()
    clock.tick()

    fps = clock.get_fps()
    if fps:
        delta = 1.0/fps

