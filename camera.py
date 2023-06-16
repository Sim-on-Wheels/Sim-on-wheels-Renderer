import glm
import numpy as np
import pygame as pg

SPEED = 0.005
SENSITIVITY = 0.04
from pyrr import Matrix44


class Camera:
    def __init__(self, app):
        self.app = app
        self.aspect_ratio = app.window_size[0] / app.window_size[1]
        self.up = glm.vec3(0, 1, 0)
        self.right = glm.vec3(1, 0, 0)
        self.forward = glm.vec3(0, 0, -1)
        self.yaw = 90
        self.pitch = 0
        # view matrix
        self.m_view = glm.mat4() #self.get_view_matrix()
        # projection matrix
        self.m_proj = self.get_projection_matrix()
        self.m_ortho_proj = Matrix44.orthogonal_projection(-12, 12, -8, 8, 0, 40, dtype='f4')

    @property
    def position(self):
        m_view = np.array(self.m_view)
        R = m_view[:3, :3]
        t = m_view[:3, -1]
        pos = R.T @ -t 
        return pos

    def rotate(self):
        rel_x, rel_y = pg.mouse.get_rel()
        self.yaw += rel_x * SENSITIVITY
        self.pitch -= rel_y * SENSITIVITY
        self.pitch = max(-89, min(89, self.pitch))

    def update_camera_vectors(self):
        yaw, pitch = glm.radians(self.yaw), glm.radians(self.pitch)

        self.forward.x = glm.cos(yaw) * glm.cos(pitch)
        self.forward.y = glm.sin(pitch)
        self.forward.z = glm.sin(yaw) * glm.cos(pitch)

        self.forward = glm.normalize(self.forward)
        self.right = glm.normalize(glm.cross(self.forward, glm.vec3(0, 1, 0)))
        self.up = glm.normalize(glm.cross(self.right, self.forward))

    def update(self):
        self.move()
        self.rotate()
        self.update_camera_vectors()
        self.m_view = self.get_view_matrix()

    def move(self):
        velocity = SPEED * self.app.clock.tick(5)
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.position += self.forward * velocity
        if keys[pg.K_s]:
            self.position -= self.forward * velocity
        if keys[pg.K_a]:
            self.position -= self.right * velocity
        if keys[pg.K_d]:
            self.position += self.right * velocity
        if keys[pg.K_q]:
            self.position += self.up * velocity
        if keys[pg.K_e]:
            self.position -= self.up * velocity

    def get_view_matrix(self):
        return glm.lookAt(self.position, self.position + self.forward, self.up)

    def get_projection_matrix(self):
        return glm.perspective(glm.radians(self.app.config.camera_config.fov),
                               self.aspect_ratio,
                               self.app.config.camera_config.near,
                               self.app.config.camera_config.far)




















