# hierarchical modeling with a robot arm

"""
How to use

left click on the blue circles, then move your mouse around to rotate the part that is selected
right click to deselect

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

    @classmethod
    def sign(self, x):
        return -1 if x < 0 else 1

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
        self.temp_rotation = self.rotation
        self.origin = origin
        self.color = color
        self.parent = parent
        self.gizmo_radius = 50
        self.mouse_last = pygame.math.Vector2()

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
            pygame.draw.polygon(surface, pygame.math.Vector3(255, 0, 0).lerp(self.color, 0.5), points, 1)

        origin = MathUtil.apply_transform(self.get_global_transform(), self.origin)
        mouse_position = pygame.math.Vector2(*pygame.mouse.get_pos())

        if selected_square is not self:
            pygame.draw.circle(surface, pygame.math.Vector3(0, 0, 100), origin, self.gizmo_radius, 2)
        else:
            pygame.draw.circle(surface, pygame.math.Vector3(255, 255, 0), origin, self.gizmo_radius, 2)
            to_mouse_last = (self.mouse_last - origin).normalize() * self.gizmo_radius
            to_mouse_cur = (mouse_position - origin).normalize() * self.gizmo_radius
            pygame.draw.line(surface, (255, 0, 0), origin, origin+to_mouse_cur, 5)
            wage_points = []
            n_wage_points = 10
            for i in range(n_wage_points + 1):
                t = i/n_wage_points
                vec = to_mouse_last.slerp(to_mouse_cur, t) + origin
                wage_points.append(vec)
            wage_points.append(origin)
            pygame.draw.polygon(surface, (255, 255, 255), wage_points)

    def update(self, delta):

        global selected_square
        if pygame.mouse.get_pressed()[0]:
            if self.mouse_inside_gizmo():
                selected_square = self
                self.temp_rotation = self.rotation
                self.mouse_last = pygame.math.Vector2(*pygame.mouse.get_pos())
        elif pygame.mouse.get_pressed()[2]:
            selected_square = None

        if selected_square is self: 
            origin = MathUtil.apply_transform(self.get_global_transform(), self.origin)
            mouse_position = pygame.math.Vector2(*pygame.mouse.get_pos())
            to_mouse_position = (mouse_position - origin).normalize()
            to_mouse_last = (self.mouse_last - origin).normalize()

            sign = -MathUtil.sign(
                    np.linalg.det(np.array([
                        [1, 1, 1],
                        [mouse_position.x, origin.x, self.mouse_last.x],
                        [mouse_position.y, origin.y, self.mouse_last.y],
                        ]))
                    )
            cdotp = to_mouse_position.dot(to_mouse_last)
            angle = 0
            try:
                angle = sign * math.acos(
                        cdotp
                        )
            except:
                pass
            self.rotation = self.temp_rotation + angle

    def mouse_inside_gizmo(self):
        origin = MathUtil.apply_transform(self.get_global_transform(), self.origin)
        mouse_position = pygame.math.Vector2(*pygame.mouse.get_pos())

        to_mouse = mouse_position - origin
        return to_mouse.dot(to_mouse) <= self.gizmo_radius**2

selected_square = None

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
    square4 = Square(
            scale=pygame.math.Vector2(30, 10),
            position=pygame.math.Vector2(-7.5, -20),
            origin=pygame.math.Vector2(15, 10),
            color=pygame.math.Vector3(0, 0, 255),
            # rotation=math.pi/4.0,
            parent=square3
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

        square1.update(delta)
        square2.update(delta)
        square3.update(delta)
        square4.update(delta)

        square1.draw(debug=debug_enabled)
        square2.draw(debug=debug_enabled)
        square3.draw(debug=debug_enabled)
        square4.draw(debug=debug_enabled)

        pygame.display.update()
        clock.tick()
        fps = clock.get_fps()
        if fps:
            delta = 1/fps


if __name__ == "__main__":
    main()
