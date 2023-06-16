import glm
import numpy as np
from .base_scenario import BaseScenario
from models.actors import StaticObjectActor

class WorldScenario(BaseScenario):

    def __init__(self, app, scenario_config):
        super().__init__(app, scenario_config)
        
        self.actors = [
            StaticObjectActor(app, self.scenario_transform, 'world_building'),
            StaticObjectActor(app, self.scenario_transform, 'world_plane')
        ]

    def get_primary_obstacle_positions(self):
        """Should not really be called, but returns world building pose"""
        building_position = self.actors[0].position
        return building_position

    def is_triggered(self):
        return False

    # to remove shadow on sentinel building
    def render_depth(self, option):
        self.actors[-1].render_depth(option)

    def render_building(self):
        self.actors[0].render()
    
    def render_plane(self):
        self.actors[1].render()



