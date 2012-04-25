import pygame
pygame.init()

from resource   import *
from grid       import *
from square     import *
from interface  import *
from imagecache import *

import unittest


def grid_action(y,x,mode):
    old = singleton_interface.get_mode()

    # perform the action on the cell
    singleton_interface.set_mode(mode)
    singleton_grid.cell_clicked((y, x))

    # restore old mode
    singleton_interface.set_mode(old)
        

class OurTests(unittest.TestCase):
    
    def setUp(self):
        ''' Method to set up the environment for the tests.  This is run before every test.'''
        # should use a standard grid and standard resource
        singleton_interface.set_mode(NORMAL)
                
        test_grid = [['G' for c in range(cols)] for r in range(rows)]
        test_grid[rows//2][cols//2] = 'H'
        test_grid[rows//2 + 1][cols//2] = 'M' 
        test_grid[rows//2 + 1][cols//2 - 1] = 'F'    
        test_grid[rows//2 + 1][cols//2 + 1] = 'S'
        test_grid[rows//2 - 1][cols//2 + 1] = 'S'
        test_grid[rows//2 + 2][cols//2 + 2] = 'S'
        test_grid[rows//2 - 1][cols//2 - 2] = 'T'
        singleton_grid.squares = [[fromString(test_grid[r][c])
                         for c in range(cols)]
                         for r in range(rows)]

    def test_resource_bank(self):
        '''Various tests to check that the resource bank behaves correctly.'''
        singleton_resource.resources['food'] = 10.0
        food1 = singleton_resource.get('food')
        self.assertFalse(singleton_resource.has({'food': 15}))
        singleton_resource.give({'food': 20.0})
        food2 = singleton_resource.get('food')
        self.assertTrue(food1 < food2)

        workers = singleton_resource.get('workers')
        self.assertFalse(singleton_resource.spend({'workers': workers + 1}))
    
    def test_building_costs_money(self):
        ''' Check that building a farm reduces the amount of money.'''
        # grab the initial resources, to see whether they go down after we build the farm.
        initial_resources = list(singleton_resource.resources.items())
        
        # send the mouse click to the grid.
        grid_action(0,0,BUILD_FARM)
        
        # make sure that the amount of wood has decreased by the cost of the building.
        cost = building_costs[BUILD_FARM]

        # for each resource, the difference should be the same as the cost.
        for resource_name, initial_value in initial_resources:
            new_value = singleton_resource.get(resource_name)
            expected_change = -cost.get(resource_name, 0)
            actual_change = new_value - initial_value
            self.assertEqual(expected_change, actual_change)
            
    def test_remove_worker_returns_to_worker_pool(self):
        ''' Check that removing a worker from a building increases the worker
        pool count by 1.'''
        initial_workers = singleton_resource.get('workers') + \
                          singleton_grid.num_workers_on_grid()
        
        for r in range(singleton_grid.rows()):
            for c in range(singleton_grid.cols()):
                grid_action(r, c, ASSIGN_WORKER)
                

        for r in range(singleton_grid.rows()):
            for c in range(singleton_grid.cols()):
                grid_action(r, c, REMOVE_WORKER)
                final_workers = singleton_resource.get('workers') + \
                        singleton_grid.num_workers_on_grid()
                self.assertEqual(initial_workers, final_workers)

    def test_destroy_building_returns_to_worker_pool(self):
        ''' Test whether destroying building returns the workers who were
        working on it to the worker pool. '''
        initial_workers = singleton_resource.get('workers') + \
                          singleton_grid.num_workers_on_grid()
        
        grid_action(0,0,BUILD_MINE)
        grid_action(0,0,ASSIGN_WORKER)
        grid_action(0,0,DESTROY_BUILDING)
        
        final_workers = singleton_resource.get('workers') + \
                        singleton_grid.num_workers_on_grid()
        
        self.assertEqual(initial_workers, final_workers)

    def test_harvest(self):
        '''Thoroughly testing harvest would require setting up lots of grids,
        which would be a lot of work. For now, we will just verify that food
        increases given test_grid.'''

        # First, we place a worker on the farm
        for row in singleton_grid.squares:
            for sq in row:
                if isinstance(sq, Farm):
                    sq.num_workers += 1

        initial_food = singleton_resource.get('food')
        singleton_grid.harvest()
        new_food = singleton_resource.get('food')
        self.assertTrue(new_food > initial_food)

    def test_image_cache(self):
        '''Check that the image cache isn't obviously broken'''
        test_img = 'tree.png'
        img1 = pygame.image.load('img/' + test_img)
        img2 = singleton_image_cache.get(test_img)
        self.assertEqual(img1.get_width(), img2.get_width())
        self.assertEqual(img1.get_height(), img2.get_height())

        # Check that the cache saves a reference to the loaded image
        # instead of wastefully reloading the image
        img3 = singleton_image_cache.get(test_img)
        self.assertEqual(img2, img3)

    def test_sublinear_productivity(self):
        '''Verify that as more workers are added to a resource, productivity per
        worker decreases'''
        tree = Tree()
        tree.num_workers = 1
        efficiency1 = tree.produce()['wood'] / tree.num_workers
        tree.num_workers = 5
        efficiency2 = tree.produce()['wood'] / tree.num_workers
        tree.num_workers = 20
        efficiency3 = tree.produce()['wood'] / tree.num_workers
        self.assertTrue(efficiency1 > efficiency2 > efficiency3)

    def test_level_progression(self):
        ''' Test that completing the level objectives increases the level.'''
        from level import levels, current_level
        self.assertEqual(current_level, 0)
        levels[current_level].update()
        self.assertEqual(current_level, 0)
        singleton_resource.give({'gold': 100000000})
        levels[current_level].update()
        from level import current_level
        self.assertEqual(current_level, 1)

    def test_level_timing(self):
        '''Assert that time remaining goes down.'''
        from level import levels, current_level
        l = levels[current_level]
        t1 = l.time_remaining
        l.update()
        t2 = l.time_remaining
        l.update()
        t3 = l.time_remaining
        self.assertTrue(t1 > t2 > t3)

    def test_sandbox_level(self):
        ''' Test that the sandbox level is unbeatable. '''
        import level
        level.current_level = len(level.levels) - 1
        self.assertTrue(isinstance(level.levels[level.current_level], level.SandboxLevel))
        # Give the player tons of gold
        singleton_resource.give({'gold': 100000000})
        level.levels[level.current_level].update()
        # This is the sandbox, so the level should not have changed
        self.assertTrue(isinstance(level.levels[level.current_level], level.SandboxLevel))

if __name__ == '__main__':
    ''' run the tests! '''
    unittest.main()

