# hierarchical modeling with a roboto arm

"""
How to use

A and D to rotate the base
W and S to rotate the lower arm
E and D to rotate the upper arm

Pass the --debug-enabled argument when running the program to enable debugging - but why would you? :|
"""
import pygame
import sys
import numpy as np
import math


class MathUtil:
    
    @classmethod
    def translate(self, position):
        return np.array([
            [1, 0, position.x],
            [0, 1, position.y],
            [0, 0, 1],
        ])

    @classmethod
    def scale(self, s):
        return np.array([
            [s.x, 0, 0],
            [0, s.y, 0],
            [0, 0, 1],
        ])

    @classmethod
    def rotate(self, angle):
        return np.array([
            [math.cos(angle), math.sin(angle), 0],
            [-math.sin(angle), math.cos(angle), 0],
            [0, 0, 1],
        ])

    @classmethod
    def apply_transform(self, tr, v):
        v_mat = np.array([v.x, v.y, 1])
        v_out = tr@v_mat
        return pygame.math.Vector2(v_out[0], v_out[1])

class Square:

    def __init__(self,
                position = pygame.math.Vector2(),
                scale=pygame.math.Vector2(1, 1),
                rotation=0,
                origin = pygame.math.Vector2(0, 0),
                color=pygame.math.Vector3(255, 255, 255),
                parent=None,
                 ):
        self.position = position
        self.scale = pygame.math.Vector2(1, 1)
        self.rotation = rotation
        self.origin = origin
        self.color = color
        self.parent = parent

        # the square itself
        self.points = [
                pygame.math.Vector2(0, 0),
                pygame.math.Vector2(scale.x, 0),
                pygame.math.Vector2(scale.x, scale.y),
                pygame.math.Vector2(0, scale.y),
                ] 

    def get_local_transform(self):
        scale = MathUtil.scale(self.scale)
        rot = MathUtil.rotate(self.rotation)
        tra = MathUtil.translate(self.position)

        to_origin = -self.origin
        to_origin_mat = MathUtil.translate(to_origin)
        tr = scale
        tr = to_origin_mat @ tr
        tr = rot @ tr
        tr = MathUtil.translate(-to_origin) @ tr
        tr = tra @ tr
        return tr


    def get_global_transform(self):
        if self.parent is None:
            return self.get_local_transform()
        
        local_transform = self.get_local_transform()
        parent_transform = self.parent.get_global_transform()
        return parent_transform @ local_transform

    def transform_points(self):

        points = []
        for i, point in enumerate(self.points):
            p = MathUtil.apply_transform(self.get_global_transform(), point)
            points.append(p)

        return points

    def draw(self, surf=None, debug=False):
        surface = pygame.display.get_surface() if surf is None else surf

        points = self.transform_points()
        pygame.draw.polygon(surface, self.color, points)
        if debug:
            for point in points:
                pygame.draw.circle(surface, (255, 255, 0), point, 5)
            pygame.draw.polygon(surface, pygame.Vector3(255, 0, 0).lerp(self.color, 0.5), points, 1)

def main():
    pygame.init()

    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Hierarchical modeling")

    square1 = Square(
            position=pygame.math.Vector2(370, 200),
            scale=pygame.math.Vector2(30, 100),
            origin=pygame.math.Vector2(15, 100),
            # rotation=math.pi/2.0,
            )

    square2 = Square(
            scale=pygame.math.Vector2(20, 50),
            position=pygame.math.Vector2(5, -60),
            color=pygame.math.Vector3(255, 0, 0),
            origin=pygame.math.Vector2(2.5, 60),
            rotation=math.pi/4.0,
            parent=square1
            )

    square3 = Square(
            scale=pygame.math.Vector2(10, 80),
            position=pygame.math.Vector2(5, -85),
            origin=pygame.math.Vector2(5, 80),
            color=pygame.math.Vector3(0, 255, 0),
            # rotation=math.pi/4.0,
            parent=square2
            )

    clock = pygame.time.Clock()
    delta = 0
    debug_enabled = False
    if sys.argv:
        if sys.argv.count("--debug-enabled"):
            debug_enabled = True

    while True:

        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        key = pygame.key.get_pressed()
        if key[pygame.K_a]:
            square1.rotation -= math.pi/2.0 * delta
        if key[pygame.K_q]:
            square1.rotation += math.pi/2.0 * delta
        if key[pygame.K_s]:
            square2.rotation -= math.pi/2.0 * delta
        if key[pygame.K_w]:
            square2.rotation += math.pi/2.0 * delta
        if key[pygame.K_d]:
            square3.rotation -= math.pi/2.0 * delta
        if key[pygame.K_e]:
            square3.rotation += math.pi/2.0 * delta
        # square1.rotation += math.pi/2.0 * delta
        if square1.rotation > math.pi/2.0:
            square1.rotation = math.pi/2.0
        elif square1.rotation < -math.pi/2.0:
            square1.rotation = -math.pi/2.0
        if square2.rotation > math.pi/2.0:
            square2.rotation = math.pi/2.0
        elif square2.rotation < -math.pi/2.0:
            square2.rotation = -math.pi/2.0
        if square3.rotation > math.pi/2.0:
            square3.rotation = math.pi/2.0
        elif square3.rotation < -math.pi/2.0:
            square3.rotation = -math.pi/2.0

        if not debug_enabled:
            square1.draw()
            square2.draw()
            square3.draw()
        else:
            square1.draw(debug=True)
            square2.draw(debug=True)
            square3.draw(debug=True)

        pygame.display.update()
        clock.tick()
        fps = clock.get_fps()
        if fps:
            delta = 1/fps


if __name__ == "__main__":
    main()
