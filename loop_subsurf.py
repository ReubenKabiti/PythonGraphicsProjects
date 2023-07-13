import pygame
import sys


pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Loop Subdivision surface in 2D")

class Point:

    def __init__(self, position, is_control_point=True):
        self.position = pygame.math.Vector2(*position)
        self.is_control_point = is_control_point
        self.radius = 5
        self.color = (255, 255, 255)

    def update(self):
        global active_point

        if active_point is self:
            self.position = pygame.math.Vector2(*pygame.mouse.get_pos()) - pygame.math.Vector2(10, 10)
        else:
            if pygame.mouse.get_pressed()[0] and self.is_mouse_inside():
                active_point = self

    def is_mouse_inside(self):
        mouse_pos = pygame.math.Vector2(*pygame.mouse.get_pos())
        pos_diff = mouse_pos - self.position
        return pos_diff.dot(pos_diff) <= self.radius**2
            
    def draw(self):
        global active_point
        if active_point is self:
            pygame.draw.circle(screen, (255, 255, 0), self.position, self.radius)
        else:
            pygame.draw.circle(screen, self.color, self.position, self.radius)

    def copy(self):
        return Point(self.position.copy(), self.is_control_point)

def draw_dotted_polygon(points, dotted=True):

    for i, point in enumerate(points):
        ind = i
        if i == len(points) - 1:
            ind = -1

        second_point = points[ind + 1]
        if not dotted:
            pygame.draw.line(screen, (255, 255, 255), second_point.position, point.position)
        else:
            pygame.draw.line(screen, (100, 100, 100), second_point.position, point.position)
        if dotted:
            point.draw()
def subdivide(points):

    if len(points) < 3:
        return points
    # add the midpoints

    points1 = []
    for i, point in enumerate(points):
        points1.append(point.copy())
        ind = i
        if i == len(points) - 1:
            ind = -1

        second_point = points[ind + 1]
        middle_point_pos = (point.position + second_point.position)/2
        middle_point = Point(position=middle_point_pos, is_control_point=False)
        points1.append(middle_point)

    for i, point in enumerate(points1):
        if not point.is_control_point:
            point.is_control_point = True
            continue

        ind_prev = i - 1
        ind_next = i + 1
        if ind_next >= len(points1):
            ind_next = 0

        point_prev = points1[ind_prev]
        point_next = points1[ind_next]
        point_new_pos = 0.25 * (point_prev.position + point_next.position) + 0.5 * point.position
        point.position = point_new_pos
        
    return points1

control_points = []
active_point = None
clock = pygame.time.Clock()

num_subdivs = 1

while True:

    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and active_point is not None:
                active_point = None
            if event.button == 3:
                if active_point is None:
                    control_points.append(Point(position=pygame.mouse.get_pos()))
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                num_subdivs -= 1
            elif event.key == pygame.K_RIGHT:
                num_subdivs += 1
            elif event.key == pygame.K_RETURN:
                if control_points:
                    control_points.pop()

    for point in control_points:
        point.update()

    if num_subdivs <= 0:
        num_subdivs = 1
    sub_points = subdivide(control_points)
    for i in range(num_subdivs - 1):
        sub_points = subdivide(sub_points)

    draw_dotted_polygon(control_points)
    draw_dotted_polygon(sub_points, dotted=False)
    pygame.display.update()
    # clock.tick(1)
