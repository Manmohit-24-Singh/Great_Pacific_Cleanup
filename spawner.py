# spawner.py
import random
from settings import *
from entities import PlasticWaste, MarineLife, Hazard, PowerUp

class Spawner:
    def __init__(self):
        self.spawn_timer = 0
        self.spawn_interval = 1.0  # Start faster
        self.difficulty_level = 0
        self.time_elapsed = 0
        
    def update(self, dt, entity_group):
        self.time_elapsed += dt
        
        # Increase difficulty
        if self.time_elapsed > DIFFICULTY_TIMER:
            self.difficulty_level += 1
            self.time_elapsed -= DIFFICULTY_TIMER
            # Smoothly reduce spawn interval with a hard cap to prevent impossible difficulty
            self.spawn_interval = max(0.4, self.spawn_interval - 0.08)
            
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_entity(entity_group)
            
    def spawn_entity(self, entity_group):
        # Choose type based on weights
        types = list(SPAWN_RATES.keys())
        weights = list(SPAWN_RATES.values())
        choice = random.choices(types, weights=weights, k=1)[0]
        
        # Spawn across a range of heights above the screen to stagger entry
        x = random.randint(50, WINDOW_WIDTH - 50)
        y = random.randint(-200, -50)
        
        if choice == 'plastic':
            ent = PlasticWaste(x, y)
        elif choice == 'marine_life':
            animal = random.choice(list(MARINE_LIFE_COLORS.keys()))
            ent = MarineLife(x, y, animal)
        elif choice == 'hazard':
            h_type = random.choice(list(HAZARD_COLORS.keys()))
            ent = Hazard(x, y, h_type)
        else: # powerup
            p_type = random.choice(list(POWERUP_COLORS.keys()))
            ent = PowerUp(x, y, p_type)
            
        entity_group.add(ent)
