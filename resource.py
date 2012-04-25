import pygame
import random
import copy
import math
from message import show_warning, render_warning


class Resource:
    # The starting resources for a level.
    default_resources = {
        'Food': 100.0,
        'Wood': 100.0,
        'Gold': 0.0,
        'Unemployed': 10,
        'Total Workers': 10
    }

    def restore_defaults(self):
        self.resources = copy.copy(Resource.default_resources)

    def __init__(self):
        ''' Initialize the current and previous resource maps, as well as the
        Font used to draw the resource text.'''
        self.restore_defaults()
        self.previous_resources = copy.copy(self.resources)
        self.font = pygame.font.SysFont("arial", 24)
        self.diff = dict((name, 0) for name in self.resources)
        self.dead_workers = 0 # keeps track of when to add a grave

    def get(self, resource_name):
        ''' Given a resource name, return how much of that resource we have.'''
        return self.resources[resource_name]

    def has(self, resource_map):
        ''' For each resource in the keys of resource_map, check whether we have
        that much.'''
        for name in resource_map:
            if self.resources[name] < resource_map[name]:
                return False
        return True

    def spend(self, resource_map):
        ''' For each resource in the keys of resource_map, reduce that resource
        count by its value in the map.'''
        if not self.has(resource_map):
            return False
        for name in resource_map:
            self.resources[name] -= resource_map[name]
        return True

    def give(self, resource_map):
        ''' Increase the resources for each resource type in the keys by the
        amount in the values of the resource_map.'''
        for name, amount in resource_map.items():
            self.resources[name] += amount

    def kill_worker(self):
        ''' Kill a worker.  Idle workers are killed first, otherwise kill a
        random worker from the grid. '''
        from grid import singleton_grid
        
        if not self.spend({'Unemployed': 1}):
            singleton_grid.kill_worker_on_grid()
        
        total_workers = self.get('Unemployed') + singleton_grid.num_workers_on_grid()
        if total_workers != 0:
            show_warning("Your workers are starving! Plant some crops and place workers on them.")
        self.dead_workers += 1
        if self.dead_workers == 4: #add a graveyard to the map
            self.dead_workers = 0
            singleton_grid.add_grave()

    def update(self):
        """Consumes some amount of food based on the number of workers"""
        from grid import singleton_grid
        
        # Feed workers.
        total_workers = self.get('Unemployed') + singleton_grid.num_workers_on_grid()
        cost = {'Food': total_workers*0.005}
        # If there isn't enough food, then kill one off.
        if not self.spend(cost) and total_workers > 0.0:
            death_rate = 0.001
            if random.random() < death_rate*total_workers:
                self.kill_worker()
            self.resources['Food'] = 0.0
        else: 
            show_warning("")
            #self.give({'food': 100}) # cannibalism
        
        # Attract workers if gold income is high. Every time they a total of 100 gold, 
        # they get an extra worker.
        min_gold_income_per_incoming_worker = 100
        
        # calculate the extra workers added
        extra_workers = (self.get('Gold') - self.previous_resources['Gold']) \
                        / min_gold_income_per_incoming_worker

        if extra_workers > 0:
            if self.get('Food') > 0:
                if self.get('Unemployed') < 5:
                    self.give({'Unemployed': extra_workers})
                    show_warning("")
                else:
                    show_warning("There are too many unemployed workers. Assign them before more people will come to your city.")
            else:
                show_warning("Your workers are starving! Build some farms and place workers on them.")  
        if self.get('Total Workers') == 0.0:
            show_warning("All of your workers have died! Now would be a good time to restart the level.")
        # update the record of past resources
        self.diff = dict(((name, self.resources[name] - self.previous_resources[name]) for name in self.resources))
        self.previous_resources = copy.copy(self.resources)

        self.enforce_worker_limit()
        self.resources['Total Workers'] = self.get_total_workers()
        
    def enforce_worker_limit(self):
        ''' Cap the worker count based on the number of house. If there are more
        than capacity, 'kill' off the extra workers (they are 'leaving' because
        there is no space).'''
        from grid import singleton_grid
        busy_workers = singleton_grid.num_workers_on_grid()
        idle_workers = self.get('Unemployed')
        total_workers = self.get_total_workers()
        capacity = singleton_grid.population_limit()
        if total_workers > capacity:
            # First, remove fractional worker, if any
            self.resources['Unemployed'] = math.floor(idle_workers)
            total_workers = busy_workers + self.get('Unemployed')
            show_warning("There is a housing crunch. Build houses before more people will come to your city.")
            # If still over capacity, kill workers
            for i in range(int(total_workers - capacity)):
                self.kill_worker()
    
    def get_total_workers(self):
        '''returns the number of idle workers plus the number of workes working'''
        from grid import singleton_grid
        busy_workers = singleton_grid.num_workers_on_grid()
        idle_workers = self.get('Unemployed')
        return busy_workers + idle_workers

    def text_color(self, name):
        ''' The color of a resource depends on the rate it is changing.'''
        if name == 'Food' and self.get('Food') == 0:
            return (255, 0, 0)
        
        diff = self.diff[name]
        if diff == 0:
            return (0,0,0)

        scale = math.log(abs(diff) + 1) * 2000
        scale = min(scale, 255)
        if diff < 0:
            return (scale, 0, 0)
        return (0, scale, 0)
        
    def paint(self, x_center, y_base):
        ''' Redraw the resource levels.'''
        screen = pygame.display.get_surface()
        for i, (name, amount) in enumerate(self.resources.items()):
            text = self.font.render(
                    "{0}: {1}".format(name, int(amount)),
                    True, self.text_color(name))
            textpos = text.get_rect(
                    centerx=x_center,
                    centery=y_base + 30*i)
            screen.blit(text, textpos)

# There is a single resource manager per game.
singleton_resource = Resource()

