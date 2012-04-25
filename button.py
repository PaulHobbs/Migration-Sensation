import os
import sys

import pygame
from pygame.locals import *

import level
from message import show_message, get_input, show_pause_menu
from constants import *


class Button(object):

    def __init__(self, x, y, label, tip=None, width=110, height=32):
        self.x = x
        self.y = y
        self.label = label
        self.width = width
        self.height = height
        self.tip = tip

        font = pygame.font.Font("arial.ttf",14)
        self.text = font.render(label, True, (0, 0, 0))
        self.textpos = self.text.get_rect(top=y+10, left=x+width/2-self.text.get_width()/2)
        self.rect = pygame.Rect(x, y, width, height)

    def tooltip(self):
        return self.tip

    def is_active(self):
        '''By default, a button has no concept of being active'''
        return False

    def activate(self):
        abstract

    def contains_point(self, point):
        '''Returns whether the given (x,y) coordinate is within our bounds.'''
        x, y = point
        return x > self.x and y > self.y \
           and x < self.x + self.width \
           and y < self.y + self.height

    def mouse_over(self):
        return self.contains_point(pygame.mouse.get_pos())

    def mouse_press(self, pos):
        ''' Signal that the mouse has clicked somewhere.  Activate the button if
        it is clicking within the button's limits.'''
        if self.contains_point(pos):
            self.activate()

    def paint(self):
        '''Updates the button display'''
        from interface import singleton_interface
        screen = pygame.display.get_surface()
        color = (200, 200, 200) if self.is_active() else (230, 230, 230)
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (150, 150, 150), self.rect, 1)
        screen.blit(self.text, self.textpos)

        # Display some helpful tip if the user is hovering over us.
        if self.mouse_over():
            singleton_interface.tip = self.tooltip()


def get_save_path(name):
    '''Convert a save name into a proper file path'''
    return 'saves/' + name + '.sav'

class SaveButton(Button):
    ''' A button for saving the level one is on. '''
    def __init__(self, x, y):
        super(SaveButton, self).__init__(x, y, 'Save Game', ['Save your progress so that you can continue this game later'])

    def activate(self):
        ''' When the save button is clicked, bring up a menu to save the level.'''
        name = get_input("What should this saved game be called? (You may want to use your first name.)")
        if name.strip() == '':
            return
        path = get_save_path(name)
        with open(path, 'w') as f:
            f.write(str(level.current_level))
            f.close()

class LoadButton(Button):
    ''' A button for loading a saved game.'''

    def __init__(self, x, y):
        super(LoadButton, self).__init__(x, y, 'Load Game', ['Load a game which you saved previously'])

    def activate(self):
        ''' When the load button is pressed, get a filename and then jump to the
        level given in the file.'''
        name = get_input("Enter the name of the saved game.")
        if name.strip() == '':
            return
        path = get_save_path(name)
        try:
            with open(path, 'r') as f:
                saved_level = int(f.read())
                level.current_level = saved_level
                level.levels[level.current_level].begin()
        except IOError:
            show_message("No save file with that name was found.")

class PauseButton(Button):
    ''' A button that pauses the game'''
    
    def __init__(self, x, y, mode=False):
        super(PauseButton, self).__init__(x, y, 'Pause Game',['Pause the game'])
        self.mode = mode
        
    def is_active(self):
        return self.mode
        
    def activate(self):
        '''When the Pause button is clicked, pause the game'''
        show_pause_menu()
            
    
            
            
class ModeButton(Button):
    ''' A button that sets and unsets an interface mode when clicked.
        mode_buttons() returns the list of buttons to create.'''
                    
    def __init__(self, x, y, label, mode, tip):
        super(ModeButton, self).__init__(x, y, label, tip)
        self.mode = mode

    def is_active(self):
        ''' a mode button is "active" if the interface mode is set to its mode.'''
        from interface import singleton_interface
        return singleton_interface.get_mode() == self.mode

    def activate(self):
        ''' toggle the mode associated with the button. '''
        from interface import singleton_interface
        if self.is_active():
            singleton_interface.set_mode(NORMAL)
        else:
            singleton_interface.set_mode(self.mode)


def mode_buttons():
    ''' A list of buttons (name, interface_mode, x_pos, y_pos, tooltip) '''
    from grid import cost_description
    return [("Build House"     , BUILD_HOUSE     , 20+130*0, 560, ("Build a house", "Cost: " + cost_description(BUILD_HOUSE))),
            ("Plant Crops"      , BUILD_FARM      , 20+130*1, 560, ("Build a farm", "Cost: "  + cost_description(BUILD_FARM))),
            ("Build Mine"      , BUILD_MINE      , 20+130*2, 560, ("Build a mine", "Cost: "  + cost_description(BUILD_MINE))),
            ("Destroy", DESTROY_BUILDING, 20+130*3, 560, ("Destroy a building",)),
            ("Assign Worker"   , ASSIGN_WORKER   , 20+130*4, 560, ("Place a worker on a resource",)),
            ("Remove Worker"   , REMOVE_WORKER   , 20+130*5, 560, ("Remove a worker from a resource",))]

