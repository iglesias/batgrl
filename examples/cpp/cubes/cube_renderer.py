'''
Original source

  github.com/salt-die/Advent-of-Code.git/2022/visuals/day_18/lava_droplet/drop_renderer.py

http://unlicense.org
'''

import numpy as np
from numpy.linalg import norm

from batgrl.gadgets.graphics import Graphics
from batgrl.gadgets.behaviors.grabbable import Grabbable

from camera import Camera

class CubeRenderer(Grabbable, Graphics):
    def __init__(self, *, aspect_ratio=True, **kwargs):
        super().__init__(**kwargs)
        self.aspect_ratio = aspect_ratio
        self.camera = Camera()
        self.cubes = []

    def on_size(self):
        super().on_size()
        self._render_cubes()

    def grab_update(self, mouse_event):
        alpha = np.pi * -mouse_event.dy / self.height
        self.camera.rotate_x(alpha)

        beta = np.pi * mouse_event.dx / self.width
        self.camera.rotate_y(beta)

        self._render_cubes()

    def _render_cubes(self):
        self.texture[:] = 0

        cam = self.camera
        cam_pos = cam.pos
        self.cubes.sort(key=lambda cube: norm(cam_pos - cube.pos), reverse=True)

        for cube in self.cubes:
            cam.render_cube(cube, self.texture, self.aspect_ratio)
