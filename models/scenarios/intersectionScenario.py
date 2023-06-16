import glm

from .base_scenario import BaseScenario, ScenarioStatus
from models.actors import CarActor, TrafficLightActor
import numpy as np
from models.utils import get_model_matrix_from_config


class IntersectionScenario(BaseScenario):

    def __init__(self, app, scenario_config):
        """
        @param:
        npc_trajectory_type: str    choose from ["turn_left", "go_straight"]
        vehicle_type:        str    choose from ["suv", "police", "sedan"]
        """
        super().__init__(app, scenario_config)
        self.trigger_distance = scenario_config['trigger_distance']
        npc_trajectory_type = scenario_config['npc_trajectory_type']
        vehicle_type = scenario_config['vehicle_type']
        self.actors = [
            CarActor(app, self.scenario_transform, vehicle_type=vehicle_type, trajectory_type=npc_trajectory_type),
            TrafficLightActor(app, self.scenario_transform),
        ]

    def get_primary_obstacle_positions(self):
        # car_position = self.actors[0].position
        car_position = self.actors[0].transform_matrix
        return [car_position]

    def is_triggered(self):
        ego_position = self.app.camera.position
        car_position = self.actors[0].position
        translation = ego_position - car_position
        distance = np.sqrt(np.sum(translation**2))
        if distance <= self.trigger_distance:
            return True
        else:
            return False
