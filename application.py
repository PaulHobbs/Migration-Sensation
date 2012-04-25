'''

Application is the entry point to our game. It is a singleton class which
controls the main game loop. It is the first object to receive input events,
although it delegates extensively to other classes when processing events. It
also has a bit of startup and shutdown code.

'''

import sys
import time

import pygame
# import pygame._view
from pygame.locals import *
from pygame.key import get_mods
pygame.init()

import interface
from interface import singleton_interface
from resource import singleton_resource
from grid import singleton_grid
from message import show_message, get_input, show_main_menu


window_size = (800, 600)
bg_color = Color(255, 255, 255)
fps = 100

class Application():

    def process_events(self):
        '''Handle any events that may have accumulated in pygame's event queue'''
        for event in pygame.event.get():
            # process mouse events
            if event.type == MOUSEBUTTONDOWN:
                singleton_grid.mouse_click(event.pos)
                singleton_interface.mouse_press(event.pos)

            # process key events
            elif event.type == KEYDOWN:
                if event.key == K_F4 and (get_mods() & KMOD_ALT):
                    sys.exit(0)
                elif event.key == K_ESCAPE:
                    singleton_interface.set_mode(interface.NORMAL)
                elif event.key == K_2 and (get_mods() & KMOD_SHIFT):
                    try:
                        code = get_input("Enter some code to execute.")
                        exec(code)
                    except Exception as e:
                        show_message(str(e))

            # process exit signals
            elif event.type == QUIT:
                pygame.quit()
                sys.exit(0)

    def logic(self):
        ''' Updates the state of the grid, resources and then updates the levels.'''
        singleton_grid.harvest()
        singleton_resource.update()


    def render(self):
        ''' Tells everything to repaint themselves'''
        # Paint the background
        screen = pygame.display.get_surface()
        screen.fill(bg_color)

        # Paint the grid
        singleton_grid.paint()

        # Paint the buttons, resources, etc.
        singleton_interface.paint()

        # Update the display
        pygame.display.flip()
        
    def check_win(self):
        '''checks if the victory conditions have been met'''
        from level import levels, current_level
        levels[current_level].update()        

    def tick(self):
        ''' Gets input, updates the state, and repaints the screen.  Basically executes one unit of game time.'''
        self.process_events() # handle any new events
        self.logic()          # perform step-by-step logic
        self.render()         # render the game
        self.check_win()      # checks if victory conditions have been met

    def start(self):   
        '''initiates the game '''
        pygame.display.set_caption("Migration Sensation")
        pygame.display.set_mode(window_size, 0) # 0 means no interesting options
        show_main_menu()
        self.loop()
        
    def loop(self):
        ''' main game loop '''
        try:
            # Main game loop
            while True:
                if not singleton_interface.pause_button.is_active():
                    self.tick()
                else:
                    self.render()         # render the game
                # Sleep for 10ms. This is a quick & dirty way to prevent the
                # game from hogging a whole CPU. Assuming that our code doesn't
                # take much time to execute, the frame rate should be around
                # 100 fps.
                time.sleep(1.0/fps)
        finally:
            # Let pygame do whatever cleanup it wants to do
            pygame.quit()
            sys.exit()
            
if __name__ == '__main__':
    Application().start()

