import pygame


class Slider:

    def __init__(self, x=0, y=0, value=0, w=100, color=(0, 255, 0)):
        self.value = value
        self.screen = pygame.display.get_surface()
        self.x = x
        self.y = y
        self.w = w
        self.padding_top = 10
        self.padding_left = 10
        self.circle_radius = 10
        self.color = color

    def get_circle_pos(self):
        value = self.value/99 # convert % to [0, 1]

        x = (1 - value) * self.x + value*(self.x + self.w) # lerp x and x+w
        y = self.y
        return (x, y)

    def update(self):
        if pygame.mouse.get_pressed()[0]:
            x, y = pygame.mouse.get_pos()
            cx, cy = self.get_circle_pos()

            if (x - cx)**2 + (y - cy)**2 <= self.circle_radius**2: # if inside the circle
                dx = x - self.x
                t = dx / self.w
                self.value = 99 * t
            elif x >= self.x and x <= self.x + self.w and abs(self.y - y) < 10: # if on the line
                dx = x - self.x
                t = dx / self.w
                self.value = 99 * t
        if self.value < 0:
            self.value = 0
        elif self.value > 99:
            self.value = 99
        
    def draw(self):

        pygame.draw.line(
            self.screen,
            (255, 255, 255),
            pygame.math.Vector2(self.x, self.y),
            pygame.math.Vector2(self.x + self.w, self.y),
            5,
        )
        pygame.draw.circle(self.screen, self.color, pygame.math.Vector2(*self.get_circle_pos()), self.circle_radius)
