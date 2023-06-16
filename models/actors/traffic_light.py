from .base_actor import Actor
from models.objects import TrafficLightObject
from pathlib import Path


class TrafficLightActor(Actor):

    def __init__(self, app, actor_transform):
        super().__init__(app, is_dynamic=False, actor_transform=actor_transform)
        self.object = TrafficLightObject(app, m_model=actor_transform)

    def step(self):
        pass

    def is_finished(self):
        return True

    def reset(self):
        pass
