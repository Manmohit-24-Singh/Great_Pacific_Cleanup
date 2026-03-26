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
        self.spawned_first_hyperdrive = False
        
    def update(self, dt, entity_group, hyperdrive=False):
        # Time and spawns move significantly faster during hyperdrive
        actual_dt = dt * (5.0 if hyperdrive else 1.0)
        self.time_elapsed += actual_dt
        
        # Increase difficulty
        if self.time_elapsed > DIFFICULTY_TIMER:
            self.difficulty_level += 1
            self.time_elapsed -= DIFFICULTY_TIMER
            # Smoothly reduce spawn interval with a hard cap to prevent impossible difficulty
            self.spawn_interval = max(0.4, self.spawn_interval - 0.08)
            
        # Guarantee a hyperdrive drop early in the run
        if self.time_elapsed >= 4.0 and not self.spawned_first_hyperdrive:
            self.spawned_first_hyperdrive = True
            x = random.randint(150, WINDOW_WIDTH - 150) # Drop closer to center
            y = random.randint(-200, -50)
            ent = PowerUp(x, y, 'hyperdrive')
            entity_group.add(ent)
            
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
            p_types = list(POWERUP_COLORS.keys())
            # Give hyperdrive a small weight compared to the standard powerups
            weights = [10 if pt != 'hyperdrive' else 2 for pt in p_types]
            p_type = random.choices(p_types, weights=weights, k=1)[0]
            ent = PowerUp(x, y, p_type)
            
        entity_group.add(ent)
