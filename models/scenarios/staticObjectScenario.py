from .base_scenario import BaseScenario
from models.actors import StaticObjectActor
import glm
import numpy as np
from models.utils import get_model_matrix_from_config

class StaticObjectScenario(BaseScenario):

    def __init__(self, app, scenario_config):
        super().__init__(app, scenario_config)

        self.actors = []
        for object_config in scenario_config['object_configs'].values():
            actor = self.parse_actor(object_config)
            self.actors.append(actor)

    def get_primary_obstacle_positions(self):
        """Assumes everything in self.actors is the primary obstacle"""
        obstacle_positions = [actor.transform_matrix for actor in self.actors]
        return obstacle_positions
        
    def parse_actor(self, config):
        object2scenrio = get_model_matrix_from_config(config['object2scenario'])
        actor_transform = self.scenario_transform * object2scenrio
        actor = StaticObjectActor(self.app, actor_transform, config['object_type'])
        return actor

    def is_triggered(self):
        return True
