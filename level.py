from random import randint
from message import show_message, show_warning

def random_grid_desc(rows, cols, square_counts):
    grid = [['G' for c in range(cols)] for r in range(rows)]
    for sq, count in square_counts.items():
        for i in range(count):
            r = randint(0, rows - 1)
            c = randint(0, cols - 1)
            while grid[r][c] != 'G':
                r = randint(0, rows - 1)
                c = randint(0, cols - 1)
            grid[r][c] = sq
    return grid

def time_description(months):
    if months == float('inf'):
        return 'infinite'
    months = int(months + .99)
    years = months // 12
    months = months % 12
    components = []
    if years > 0:
        components.append("{0} year{1}".format(years, '' if years == 1 else 's'))
    if months > 0:
        components.append("{0} month{1}".format(months, '' if months == 1 else 's'))
    return ', '.join(components)

class Level(object):
    def __init__(self, duration, gold_goal, population_goal, square_counts):
        from grid import rows, cols
        self.duration = duration
        self.gold_goal = gold_goal
        self.population_goal = population_goal
        self.grid = random_grid_desc(rows, cols, square_counts)

    def begin(self):
        from grid import singleton_grid, grid_from_description
        from resource import singleton_resource
        singleton_grid.squares = grid_from_description(self.grid)
        self.time_remaining = self.duration
        singleton_resource.restore_defaults()
        show_warning("")

    def update(self):
        from resource import singleton_resource
        global current_level
        # Check if victory condition has been met
        bool0 = singleton_resource.get_total_workers() >= self.population_goal
        bool1 = singleton_resource.get('Gold') >= self.gold_goal
        if (bool0 and bool1):
            try:
                current_level += 1
                levels[current_level].begin()
                show_message("You have conquered this level! Next is level {0}.".format(current_level + 1))
            except IndexError:
                show_message("You have beaten each level in the game! We will now take you back to the first level.")
                current_level = 0
                levels[current_level].begin()

        # Check if player has run out of time
        self.time_remaining -= 0.01
        if self.time_remaining <= 0:
            # Restart the current level
            show_message("Oh no, you have run out of time!")
            levels[current_level].begin()

class SandboxLevel(Level):
    def __init__(self, square_counts): ## crashed for unknown reason. Switched to the type(self) thing
        super(SandboxLevel, self).__init__(None, None, None, square_counts)

    def begin(self):
        super(SandboxLevel, self).begin()
        show_warning("You're on your own, now. Have fun.")

    def update(self):
        pass

levels = (
    Level(15*12, 200, 10, {'H': 2, 'M': 1, 'F': 1, 'S': 2, 'T': 2}),
    Level(8*12, 1500, 20, {'H': 1, 'M': 1, 'F': 1, 'S': 5, 'T': 5}),
    Level(5*12, 3000, 30, {'H': 1, 'M': 1, 'F': 1, 'S': 5, 'T': 3}),
    Level(5*12, 5000, 40, {'H': 1, 'M': 1, 'F': 1, 'S': 5, 'T': 3}),
    Level(6*12, 7000, 60, {'H': 1, 'M': 0, 'F': 0, 'S': 2, 'T': 2}),
    Level(10*12, 30000, 180 , {'H': 1, 'M': 0, 'F': 0, 'S': 0, 'T': 2}),
    SandboxLevel({'H': 1, 'T': 2}),
#    SandboxLevel({'H': 20, 'M': 20, 'F': 20, 'S': 5, 'T': 5}) # boundry case debug level
)

def goto_level(n):
    global current_level
    current_level = n
    levels[n].begin()

current_level = 0
levels[current_level].begin()

