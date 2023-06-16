from abc import ABC, abstractmethod
import numpy as np


class Actor(ABC):

    def __init__(self, app, is_dynamic, actor_transform):
        self.app = app
        self.object = None
        self.actor_transform = actor_transform
        self.curr_step = 0
        self.is_dynamic = is_dynamic
    
    @property
    def position(self):
        return self.object.position

    @property
    def transform_matrix(self):
        return self.object.transform_matrix

    @abstractmethod
    def step(self): ...

    @abstractmethod
    def is_finished(self): ...

    def reset(self):
        self.curr_step = 0

    def render(self):
        self.object.render()

    def render_depth(self, option="from_light"):
        """
        @option: str    choose from ["from_light", "from_fpv"]
        """
        if option == 'from_light':
            self.object.render_depth(m_view_light=self.app.light.m_view_light,
                                                     m_proj=self.app.camera.m_ortho_proj)
        elif option == 'from_fpv':
            self.object.render_depth(m_view_light=self.app.camera.m_view,
                                                     m_proj=self.app.camera.m_proj)
        else:
            raise NotImplementedError

