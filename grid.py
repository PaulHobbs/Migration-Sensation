import random
import pygame
from square import *

grid_size = rows, cols = (11, 12)

buildings = {
    BUILD_HOUSE: House,
    BUILD_MINE: Mine,
    BUILD_FARM: Farm
}

building_costs = {
    BUILD_HOUSE: {'Wood': 50},
    BUILD_MINE: {'Wood': 50, 'Food': 20},
    BUILD_FARM: {'Wood': 35}
}

def cost_description(blding):
    cost_map = building_costs[blding]
    description_parts = ["{0} {1}".format(amt, name) for name, amt in cost_map.items()]
    return ', '.join(description_parts)

def grid_from_description(desc):
    return [[fromString(sq) for sq in row] for row in desc]

class Grid:
    cell_width = cell_height = 50

    def __init__(self):
        pass

    def rows(self):
        return len(self.squares)

    def cols(self):
        return len(self.squares[0])

    def num_houses(self):
        ''' Returns the number of houses on the grid.'''
        n = 0
        for row in self.squares:
            for sq in row:
                if isinstance(sq, House):
                    n += 1
        return n

    def population_limit(self):
        return self.num_houses() * 10

    def get_mouse_cell(self, pos):
        ''' takes a mouse position and translates that into a cell in the grid. '''
        mouse_x, mouse_y = pos
        c = mouse_x // Grid.cell_width
        r = mouse_y // Grid.cell_height
        if c < self.cols() and r < self.rows():
            return (r, c)
        return None

    def mouse_click(self, pos):
        ''' The user clicked the mouse, so check whether it was on a cell in the
        grid.  If so, tell that cell that it was clicked.'''
        mouse_cell = self.get_mouse_cell(pos)
        if mouse_cell is not None:
            r, c = mouse_cell
            self.cell_clicked((r, c))

    def cell_clicked(self, pos):
        ''' Method runs when the user clicks on a cell in the grid.'''
        from interface import singleton_interface        
        from resource  import singleton_resource
        
        r,c = pos

        # check for building construction
        if self.squares[r][c].buildable():
            try:
                mode = singleton_interface.get_mode()
                cost = building_costs[mode]
                if singleton_resource.spend(cost):
                    self.squares[r][c] = buildings[mode]()
            except KeyError:
                pass

        # check for worker assigning;
        if self.squares[r][c].workable():
            # if we want to assign a worker, we have to have one available.
            if singleton_interface.get_mode() == ASSIGN_WORKER \
                       and singleton_resource.get('Unemployed') >= 1 \
                       and self.squares[r][c].num_workers < 5:
                # then use up the worker and assign it to the square
                self.squares[r][c].num_workers += 1
                singleton_resource.resources['Unemployed'] -= 1
            if singleton_interface.get_mode() == REMOVE_WORKER \
                       and self.squares[r][c].num_workers > 0:
                self.squares[r][c].num_workers -= 1
                singleton_resource.resources['Unemployed'] += 1

        # demolish a building if requested
        if singleton_interface.get_mode() == DESTROY_BUILDING:
            self.demolish(r,c)
    
    def demolish(self, r, c):     
        from resource  import singleton_resource
        '''attempts to demolish a building. Returns True if a building is sucessfully demolished'''
        if self.squares[r][c].destroyable() and (self.num_houses() > 1 or not (isinstance(self.squares[r][c], House))):
            # Free the workers
            singleton_resource.give({'Unemployed': self.squares[r][c].num_workers})
            # Replace building with grass patch
            self.squares[r][c] = Grass()
            return True
        return False
            
    def is_full(self):
        '''returns true if every elt on the grid is filled'''
        for row in self.squares:
            for square in row:
                if isinstance(square, Grass):
                    return False
        return True
    
    def destroyables(self):     
        tally = 0
        for row in self.squares:
            for square in row:
                if square.destroyable():
                    tally += 1
        return tally
    def add_grave(self):
        '''adds a grave to the map. If there are no available squares it destrays a random destroyable building'''
        from message import show_warning
        if self.num_houses() != 0:
            not_assigned = True
            if self.is_full():
                while not_assigned:
                    r = random.randint(0, rows-1)
                    c = random.randint(0,cols-1)
                    if self.squares[r][c].destroyable() or self.destroyables < 2:
                        if self.demolish(r,c):
                            self.squares[r][c] = Grave()
                            not_assigned = False
            else:
                while not_assigned:
                    r = random.randint(0, rows-1)
                    c = random.randint(0,cols-1)
                    if self.squares[r][c].buildable():
                        self.squares[r][c] = Grave()
                        not_assigned = False
        else:
            from message import show_warning
            show_warning("Your whole town is one big Cemetery! This might be a good time to restart the level.")
            
            
    def harvest(self):
        ''' Called once per tick.  Updates the resources based on the production of the buildings in the grid.'''
        from resource import singleton_resource
        for row in self.squares:
            for square in row:
                singleton_resource.give(square.produce())

    def num_workers_on_grid(self):
        '''Returns the number of workers on the grid.  Useful for counting how
        much food they eat.'''
        total = 0
        for row in self.squares:
            for square in row:
                total += square.num_workers
        return total

    def kill_worker_on_grid(self):
        '''selects a random worker on the grid and "eliminates" it".  This
        happens when the population is starving and there are no idle workers to
        kill.'''

        # the number of workers left to consider
        n = self.num_workers_on_grid()
        for row in self.squares:
            for square in row:
                # the chance that we should choose one of the workers on the
                # current square
                if isinstance(square, Farm) and n > 1: # don't remove farmers if we don't have to
                    p = 0.0
                else:
                    try:
                        p = float(square.num_workers) / n
                    except ZeroDivisionError:
                        p = 0.0
                    if random.random() < p:
                        square.num_workers -= 1
                        return
                # if we don't pick a worker on the current square, reduce the
                # number of workers left to consider
                n -= square.num_workers

    def paint(self):
        ''' Update the display of the grid. ''' 
        screen = pygame.display.get_surface()


        # paint each square
        for r, row in enumerate(self.squares):
            for c, sq in enumerate(row):
                sq.paint(c*Grid.cell_width, r*Grid.cell_height,
                        Grid.cell_width, Grid.cell_height)
                
        # paint the lines between squares
        grid_w = Grid.cell_width * self.cols()
        grid_h = Grid.cell_height * self.rows()
        line_color = (170, 200, 170)
        for r in range(self.rows() + 1):
            y = Grid.cell_height * r
            pygame.draw.line(screen, line_color,
                (0, y), (grid_w, y))
        for c in range(self.cols() + 1):
            x = Grid.cell_width * c
            pygame.draw.line(screen, line_color,
                (x, 0), (x, grid_h))


# There is only one instance of Grid per game.
singleton_grid = Grid()

