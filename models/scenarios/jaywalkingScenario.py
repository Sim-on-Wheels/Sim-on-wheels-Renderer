from .base_scenario import BaseScenario
from models.actors import PersonActor
import glm
import numpy as np
from models.utils import get_model_matrix_from_config

class JaywalkingScenario(BaseScenario):

    def __init__(self, app, scenario_config):
        """
        @param:
        npc_type:               str    choose from ["man", "woman"]
        """
        super().__init__(app, scenario_config)
        actor_configs = scenario_config['actor_configs']
        self.trigger_distance = scenario_config['trigger_distance']
        self.actors = []
        for actor_config in actor_configs.values():
            object2scenario = get_model_matrix_from_config(actor_config['object2scenario'])
            actor = PersonActor(
                app, 
                actor_transform=self.scenario_transform * object2scenario,
                animation_type=actor_config['animation_type']
            )
            self.actors.append(actor)

    def get_primary_obstacle_positions(self):
        """Assumes everything in self.actors is a primary obstacle"""
        obstacle_positions = [actor.transform_matrix for actor in self.actors]
        return obstacle_positions

    def is_triggered(self):
        ego_position = self.app.camera.position
        actor_positions = [actor.position for actor in self.actors]
        actor_positions = np.stack(actor_positions)

        translation = actor_positions - ego_position[None]
        distance = np.sqrt(np.sum(translation**2, axis=1))
        if distance.min() <= self.trigger_distance:
            return True
        else:
            return False