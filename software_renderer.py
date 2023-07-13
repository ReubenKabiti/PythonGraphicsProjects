import pygame
import numpy as np
import math
import sys
from slider import Slider
pygame.init()


SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
light_dir = np.array([-1, 0, -1])
light_dir = light_dir / math.sqrt(light_dir.dot(light_dir))

def create_obj_txt(verts, inds):

    txt = ""
    for i, vert in enumerate(verts):
        if i%3 == 0:
            txt += "\nv"
        txt += f" {vert}"
    txt += "\n"
    for i, ind in enumerate(inds):
        if i%3 == 0:
            txt += "\nf"
        txt += f" {ind + 1}"
    return txt

def read_obj(filename):
    data = ""
    vertices = []
    indices = []
    try:
        with open(filename, "r") as file:
            data = file.read()
    except:
        print(f"{filename} not found")
        return (None, None)

    lines = data.split("\n")
    for line in lines:
        # if not line or line.startswith("o") or line.startswith("#"):
        #     continue
        blocks = line.split(" ")
        if line.startswith("v"):
            for i in range(1, 4):
                vertices.append(float(blocks[i]))
        elif line.startswith("f"):
            for i in range(1, 4):
                indices.append(int(blocks[i]) - 1)
    return (vertices, indices)

class Camera:

    def __init__(self, fov, aspect_ratio, near, far, position):
        self.fov = fov
        self.aspect_ratio = aspect_ratio
        self.near = near
        self.far = far
        self.position = position
    
    def project_point(self, point):
        x = point[0]
        y = point[1]
        z = point[2]

        if self.position[2] - z < self.near:
            return

        flen = self.aspect_ratio/(2*math.tan(self.fov))
        x = x*flen/(self.position[2]-z) / self.aspect_ratio
        y = y*flen/(self.position[2]-z)
        return (x, y)
    
def ntos(point):
    x = point[0]
    y = point[1]
    x = (x + 1)/2 * SCREEN_WIDTH
    y = (1 - y)/2 * SCREEN_HEIGHT
    return (int(x), int(y))

def create_rot_mat(angle):
    rot_1 = np.array([
        [math.cos(angle),  0, math.sin(angle)],
        [0,                1,               0],
        [-math.sin(angle), 0, math.cos(angle)],
    ])

    rot_2 = np.array([
        [1, 0, 0],
        [0, math.cos(angle), math.sin(angle)],
        [0, -math.sin(angle), math.cos(angle)],
    ])
    rot = rot_1@rot_2
    return rot

def create_scale_mat(scale):
    mat = np.array([
        [scale[0],      0,               0],
        [0,             scale[1],        0],
        [0,             0,        scale[2]],
    ])
    return mat

def apply_transform(points, tr):
    ps = []
    for point in points:
        ps.append(tr@point)
    return ps


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("rotating cube")

def project_all_tris(cam, verts, inds, angle=0, scale=(1, 1, 1)):
    tris = []
    i = 0
    while i < len(inds) - 2:
        v1 = np.array([verts[3*inds[i]], verts[3*inds[i]+1], verts[3*inds[i]+2]])
        v2 = np.array([verts[3*inds[i+1]], verts[3*inds[i+1]+1], verts[3*inds[i+1]+2]])
        v3 = np.array([verts[3*inds[i+2]], verts[3*inds[i+2]+1], verts[3*inds[i+2]+2]])
        v1, v2, v3 = apply_transform((v1, v2, v3), create_scale_mat(scale))
        v1, v2, v3 = apply_transform((v1, v2, v3), create_rot_mat(angle))
        p1 = cam.project_point(v1)
        p2 = cam.project_point(v2)
        p3 = cam.project_point(v3)
        if p1 is None or p2 is None or p3 is None:
            i += 3
            continue
        facing_mat = np.array([
            [1,         1,          1],
            [p1[0],     p2[0],  p3[0]],
            [p1[1],     p2[1],  p3[1]]
        ])
        if np.linalg.det(facing_mat) <= 0: # cull back-faces and collinear points
            i += 3
            continue
        tris.append([p1, p2, p3, v1, v2, v3])
        i += 3
    return tris

def draw_tris(cam, verts, inds, angle=0, line_width=0, color=(255, 0, 0), scale=(1, 1, 1)):
    tris = project_all_tris(cam, verts, inds, angle, scale)
    for tri in tris:
        p1, p2, p3, v1, v2, v3 = tri
        p1 = ntos(p1)
        p2 = ntos(p2)
        p3 = ntos(p3)
        v2v3 = v3-v2
        v2v1 = v1-v2
        normal = np.cross(v2v3, v2v1)
        if normal.dot(normal) == 0:
            continue
        normal /= math.sqrt(normal.dot(normal))
        f = normal.dot(-light_dir)
        f = 0 if f < 0 else f
        c = [min(int(col * f), 255) for col in color]
        pygame.draw.polygon(screen, c, (p1, p2, p3), line_width)

camera = Camera(
        math.pi/4.0,
        SCREEN_WIDTH/SCREEN_HEIGHT,
        0.1,
        1000.0,
        np.array([0, 0, 3])
)


clock = pygame.time.Clock()
delta = 0
angle = 0

bg_start_color = pygame.math.Vector3(0, 0, 50)
bg_end_color = pygame.math.Vector3(50, 50, 50)
def create_bg():
    n = 50 # number of horizontal rects
    bg = pygame.surface.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    y = 0
    for i in range(n):
        t = i / n
        color = bg_start_color.lerp(bg_end_color, t)
        pygame.draw.rect(bg, color, pygame.Rect((0, y), (SCREEN_WIDTH, SCREEN_HEIGHT//n)))
        y += SCREEN_HEIGHT//n
    return bg

bg = create_bg()
slider_x = Slider(x=10, y=10, color=(255, 0, 0), value=50)
slider_y = Slider(x=10, y=40, color=(0, 255, 0), value=50)
slider_z = Slider(x=10, y=70, color=(0, 0, 255), value=50)
slider_rot = Slider(x=10, y=100, color=(255, 255, 0))
slider_wireframe = Slider(x=50, y=130, color=(0, 0, 0), w=20)

vertices = [
        -0.5, 0.5, 0,
        0.5, 0.5, 0,
        0.5, -0.5, 0,
        -0.5, -0.5, 0,

        -0.5, 0.5, -1,
        0.5, 0.5, -1,
        0.5, -0.5, -1,
        -0.5, -0.5, -1
]
indices = [
        3, 1, 0,
        3, 2, 1,

        7, 4, 5,
        7, 5, 6,

        3, 0, 4,
        3, 4, 7,

        1, 2, 5,
        2, 6, 5,

        0, 5, 4,
        0, 1, 5,

        3, 7, 2,
        7, 6, 2

]

# vertices, indices = read_obj("gear.obj")

scale = (1, 1, 1)

def freeze_transformations():
    global scale
    global vertices
    global slider_x
    global slider_y
    global slider_z
    scale_mat = create_scale_mat(scale)

    verts_new = []
    # transform the vertices
    i = 0
    while i < len(vertices) - 2:
        vertex = np.array([vertices[i], vertices[i + 1], vertices[i + 2]])
        vertex_transformed = scale_mat@vertex
        verts_new.append(vertex_transformed[0])
        verts_new.append(vertex_transformed[1])
        verts_new.append(vertex_transformed[2])
        i += 3

    # reset the sliders
    slider_x.value = 50
    slider_y.value = 50
    slider_z.value = 50

    # set the vertices
    vertices = verts_new

while True:

    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.WINDOWRESIZED:
            SCREEN_WIDTH = screen.get_rect().width
            SCREEN_HEIGHT = screen.get_rect().height
            camera.aspect_ratio = SCREEN_WIDTH/SCREEN_HEIGHT
            bg = create_bg()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                obj_txt = create_obj_txt(vertices, indices)
                with open("out.obj", "w") as file:
                    file.write(obj_txt)

    slider_x.update()
    slider_y.update()
    slider_z.update()
    slider_rot.update()
    slider_wireframe.update()
    key = pygame.key.get_pressed()
    if key[pygame.K_RETURN]:
        freeze_transformations()

    screen.blit(bg, (0, 0))
    angle = slider_rot.value / 99 * 2 * math.pi
    scale = (slider_x.value/100 * 2, slider_y.value/100 * 2, slider_z.value/100 * 2)
    draw_tris(camera, vertices, indices, angle=angle, line_width=0, color=(255, 255, 255), scale=scale)
    if slider_wireframe.value > 50:
        slider_wireframe.value = 99
        slider_wireframe.color = (0, 0, 255)
        draw_tris(camera, vertices, indices, angle, 1, (0, 0, 255), scale)
    else:
        slider_wireframe.value = 0
        slider_wireframe.color = (100, 100, 100)
    slider_x.draw()
    slider_y.draw()
    slider_z.draw()
    slider_rot.draw()
    slider_wireframe.draw()
    pygame.display.update()
    clock.tick()
    fps = clock.get_fps()
    if fps:
        delta = 1 / fps
    # angle += rot_speed*delta
