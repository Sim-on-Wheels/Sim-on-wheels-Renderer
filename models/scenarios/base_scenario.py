from enum import Enum
from abc import ABC, abstractmethod
from models.actors.base_actor import Actor
from models.utils import get_model_matrix_from_config


class ScenarioStatus(Enum):
    PENDING = 1
    RUNNING = 2


class BaseScenario(ABC):
    def __init__(self, app, scenario_config):
        self.app = app
        self.scenario_config = scenario_config
        self.scenario_transform = get_model_matrix_from_config(scenario_config['scenario2world'])
        self.status = ScenarioStatus.PENDING
        self.actors = []

    def start(self):
        self.status = ScenarioStatus.RUNNING

    def is_finished(self):
        is_finished = True

        for actor in self.actors:
            is_finished = is_finished and actor.is_finished()
        if is_finished:
            self.status = ScenarioStatus.PENDING
        return is_finished

    def reset(self):
        self.status = ScenarioStatus.PENDING
        for actor in self.actors:
            actor.reset()

    def render(self):
        for actor in self.actors:
            actor.render()

    def render_depth(self, option):
        for actor in self.actors:
            actor.render_depth(option)

    @abstractmethod
    def is_triggered(self):
        pass
    
    @abstractmethod
    def get_primary_obstacle_positions(self):
        pass

    def update(self):
        if self.status == ScenarioStatus.PENDING:
            if self.is_triggered():
                self.start()
        if self.status == ScenarioStatus.PENDING:
            return
        for actor in self.actors:
            actor.step()
        if self.is_finished():
            self.reset()








