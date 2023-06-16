from .base_actor import Actor
from models.objects import CarObject
from models.objects import BenzObject
from models.objects import BusObject
import numpy as np
import glm
from constants import T_blender2opengl


class CarActor(Actor):

    def __init__(self, app, actor_transform, vehicle_type, trajectory_type):
        super().__init__(app, is_dynamic=True, actor_transform=actor_transform)
        self.trajectory = self.load_trajectory(trajectory_type)
        self.trajectory_i = 0
        self.m_model = actor_transform * self.get_vehicle_transform()
        self.object = self.load_vehicle(app, vehicle_type)

    def get_vehicle_transform(self):
        m_model = self.trajectory[self.trajectory_i % len(self.trajectory)]
        m_model = T_blender2opengl @  m_model
        return glm.mat4(m_model)

    def load_vehicle(self, app, vehicle_type):
        if vehicle_type == 'suv':
            return CarObject(app, m_model=self.m_model)
        elif vehicle_type == 'benz':
            return BenzObject(app, m_model=self.m_model)
        elif vehicle_type == 'bus':
            return BusObject(app, m_model=self.m_model)
        else:
            raise NotImplementedError

    def load_trajectory(self, trajectory_type):
        if trajectory_type == 'turn_left':
            return np.load('assets/trajectories/vehicle_turn_left.npy')
        elif trajectory_type == 'go_straight':
            return np.load('assets/trajectories/vehicle_go_straight.npy')
        elif trajectory_type == 'in_front':
            return np.load('assets/trajectories/vehicle_in_front.npy')
        else:
            raise NotImplementedError

    def step(self):
        self.trajectory_i = self.trajectory_i + 1
        m_model = self.actor_transform * self.get_vehicle_transform()
        self.object.update_pose(m_model)

    def is_finished(self):
        return self.trajectory_i == len(self.trajectory)

    def reset(self):
        self.trajectory_i = 0