from .base_actor import Actor
from pathlib import Path
from models.objects import *

class StaticObjectActor(Actor):

    def __init__(self, app, actor_transform, object_type='cone'):
        super().__init__(app, is_dynamic=False, actor_transform=actor_transform)
        if object_type == 'world_plane':
            self.object = WorldPlaneObject(app, m_model=actor_transform)
        elif object_type == 'world_building':
            self.object = WorldBuildingObject(app, m_model=actor_transform)
        elif object_type == 'cone':
            self.object = ConeObject(app, m_model=actor_transform)
        elif object_type == 'suv':
            self.object = CarObject(app, m_model=actor_transform)
        elif object_type == 'baby':
            self.object = BabyObject(app, m_model=actor_transform)
        elif object_type == 'benz':
            self.object = BenzObject(app, m_model=actor_transform)
        elif object_type == 'bus':
            self.object = BusObject(app, m_model=actor_transform)
        elif object_type == 'traffic_light':
            self.object = TrafficLightObject(app, m_model=actor_transform)
        elif object_type == 'building':
            self.object = BuildingObject(app, m_model=actor_transform)
        elif object_type == 'yuan':
            self.object = ScannedObject(app, 'yuan', m_model=actor_transform)
        elif object_type == 'albert':
            self.object = ScannedObject(app, 'albert', m_model=actor_transform)
        elif object_type == 'chair_0':
            self.object = ScannedObject(app, 'chair_0', m_model=actor_transform)
        elif object_type == 'chair_1':
            self.object = ScannedObject(app, 'chair_1', m_model=actor_transform)
        elif object_type == 'sim_cone':
            self.object = ScannedObject(app, 'cone', m_model=actor_transform)
        elif object_type == 'ladder':
            self.object = ScannedObject(app, 'ladder', m_model=actor_transform)
        elif object_type == 'zhi-hao':
            self.object = ScannedObject(app, 'zhi-hao', m_model=actor_transform)
        elif object_type == 'real_bench':
            self.object = ScannedObject(app, 'reality/bench', m_model=actor_transform)
        elif object_type == 'real_chair_b':
            self.object = ScannedObject(app, 'reality/chair_b', m_model=actor_transform)
        elif object_type == 'real_chair_o':
            self.object = ScannedObject(app, 'reality/chair_o', m_model=actor_transform)
        elif object_type == 'real_ladder':
            self.object = ScannedObject(app, 'reality/ladder', m_model=actor_transform)
        elif object_type == 'real_cone':
            self.object = ScannedObject(app, 'reality/cone', m_model=actor_transform)
        elif object_type == 'real_trolley':
            self.object = ScannedObject(app, 'reality/trolley', m_model=actor_transform)
        elif object_type == 'real_yuan':
            self.object = ScannedObject(app, 'reality/yuan', m_model=actor_transform)
        elif object_type == 'real_zhihao':
            self.object = ScannedObject(app, 'reality/zhihao', m_model=actor_transform)        
        else:
            raise NotImplementedError

    def step(self):
        pass

    def reset(self):
        pass

    def is_finished(self):
        return True
