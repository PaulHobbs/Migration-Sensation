import pygame
from resource import singleton_resource
from button import *
from constants import *
from message import render_warning, word_wrap, width_warning, current_warning


class Interface:
    cursor_map = {
        NORMAL           : pygame.image.load('img/normal.png'),
        BUILD_HOUSE      : pygame.image.load('img/house.png'),
        BUILD_FARM       : pygame.image.load('img/farm.png'),
        BUILD_MINE       : pygame.image.load('img/mine.png'),
        DESTROY_BUILDING : pygame.image.load('img/remove worker.png'),
        ASSIGN_WORKER    : pygame.image.load('img/assign worker.png'),
        REMOVE_WORKER    : pygame.image.load('img/remove worker.png')
    }

    def __init__(self):
        ''' Initialize an interface by creating the Mode buttons and the fonts
        for tooltips, level and time.  Set the default mode to be NORMAL,
        i.e. no button is activated.'''
        self.buttons = []
        for label, mode, x, y, tip in mode_buttons():
            btn = ModeButton(x, y, label, mode, tip)
            self.buttons.append(btn)

        self.pause_button = PauseButton(650, 180)
        self.buttons.append(self.pause_button)

        self.__mode__ = NORMAL
        self.tip = None
        self.font_tips = pygame.font.SysFont("arial", 20)
        self.font_level = pygame.font.SysFont("arial", 28)
        self.font_time = pygame.font.SysFont("arial", 14)

    def get_mode(self):
        return self.__mode__

    def set_mode(self, mode): 
        """set_mode sets the interface mode to the given value (which is a
        number in the enum given above).  Any active buttons are deactivated."""
        self.__mode__ = mode

    def mouse_press(self, pos):
        ''' The user pressed the mouse.  Check whether it pressed one of our buttons!'''
        for btn in self.buttons:
            btn.mouse_press(pos)

    def draw_tooltip(self, tip):
        ''' If the user is hovering over a button with a tooltip, this method is
        called.  It renders some help text next to the cursor.'''
        screen = pygame.display.get_surface()
        texts = [self.font_tips.render(line, True, (0, 0, 0)) for line in tip]
        w = max(line.get_width() for line in texts)
        h = sum(line.get_height() for line in texts)
        all_text = pygame.Surface((w, h), pygame.SRCALPHA)
        y = 0
        for line in texts:
            all_text.blit(line, (0, y))
            y += line.get_height()

        # make sure that the text isn't drawn outside of the screen.
        x, y = pygame.mouse.get_pos()
        if x + all_text.get_width() > screen.get_width():
            x -= all_text.get_width()
        if y + all_text.get_height() > screen.get_height():
            y -= all_text.get_height()

        PADDING = 3
        x_padded = x - PADDING
        y_padded = y - PADDING
        w_padded = w + 2*PADDING
        h_padded = h + 2*PADDING

        pygame.draw.rect(screen, (240, 240, 200), (x_padded, y_padded, w_padded, h_padded))
        pygame.draw.rect(screen, (100, 100, 100), (x_padded, y_padded, w_padded, h_padded), 1)
        screen.blit(all_text, (x, y))

    def paint(self, flag = True):
        ''' Redraw all the buttons, the level help, the cursor, and maybe draw a tooltip.'''
        from level import levels, current_level, time_description, SandboxLevel
        screen = pygame.display.get_surface()
        lvl = levels[current_level]

        x_center = screen.get_width() - 100
        singleton_resource.paint(x_center, 250)

        txt = "Level {0}".format(current_level + 1)
        txt = self.font_level.render(txt, True, (0, 0, 0))
        screen.blit(txt, txt.get_rect(centerx=x_center, centery=40))

        # Draw the level help text.
        if isinstance(lvl, SandboxLevel):
            txt = ["\"The point is that"]
        else:
            txt = word_wrap("Raise {0} gold and have {1} workers in {2}".format(lvl.gold_goal, lvl.population_goal, time_description(lvl.duration)), width_warning, self.font_time)
        txt.append("")
        lines = [self.font_time.render(line, True, (0, 0, 0)) for line in txt]
        height = sum([l.get_height() for l in lines])
        y = 100 - height/2
        x = screen.get_width() - width_warning
        for line in lines:
            screen.blit(line, (x,y))
            y += line.get_height()
        if isinstance(lvl, SandboxLevel):
            txt = "there ain't no point.\""
        else:
            txt = "{0} remaining".format(time_description(lvl.time_remaining))
        txt = self.font_time.render(txt, True, (0, 0, 0))
        screen.blit(txt, txt.get_rect(centerx=x_center, centery=120))

        for btn in self.buttons:
            btn.paint()

        # Paint the cursor.
        if flag:
            self.paint_cursor()
        
        render_warning()

        if self.tip is not None and flag:
            self.draw_tooltip(self.tip)
            self.tip = None
    
    def paint_cursor(self):
    
        screen = pygame.display.get_surface()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        cursor_img = Interface.cursor_map[self.__mode__]
        cursor_x = mouse_x - cursor_img.get_width()/2
        cursor_y = mouse_y - cursor_img.get_height()/2
        screen.blit(cursor_img, (cursor_x, cursor_y))
    
            
    

singleton_interface = Interface()
pygame.mouse.set_visible(False)
