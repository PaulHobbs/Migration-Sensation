'''
This module defines functions for displaying messages and warnings. Showing a
message pauses the game until the user acknowledges the message. Showing a
warning causes it to appear in a small box in the interface, but does not grab
the user's attention by pausing the game.

There is also a function called get_input. This behaves like show_message,
except that it also prompts the user to enter a string and returns this string.

These methods are surprisingly non-trivial, partly because pygame has no
built-in logic for rendering strings which span multiple lines.
'''

import pygame
from pygame.locals import *
import time
import sys
from imagecache import singleton_image_cache


default_cursor = ((16, 19), (0, 0), (128, 0, 192, 0, 160, 0, 144, 0, 136, 0, 132, 0, 130, 0, 129, 0, 128, 128, 128, 64, 128, 32, 128, 16, 129, 240, 137, 0, 148, 128, 164, 128, 194, 64, 2, 64, 1, 128), (128, 0, 192, 0, 224, 0, 240, 0, 248, 0, 252, 0, 254, 0, 255, 0, 255, 128, 255, 192, 255, 224, 255, 240, 255, 240, 255, 0, 247, 128, 231, 128, 195, 192, 3, 192, 1, 128))
bg_color = Color(255, 255, 255)
# The font to be used for messages
font_msg = pygame.font.SysFont("arial", 24)

# The font to be used for warnings
font_warning = pygame.font.SysFont("arial", 16)

# The width of the message box
width_msg = 400
# The width of the warning box
width_warning = 160


def word_wrap(s, width, font):
    '''Given some (potentially long) string, split up the string into
    a list of lines that will fit into the specified width.'''
    try:
        words = s.split()
        lines = [words[0]]
        for w in words[1:]:
            new_line = lines[-1] + " " + w # what the last line will look like
            if font.render(new_line, True, (0, 0, 0)).get_width() > width:
                # The last line has grown too long, so start a new line.
                lines.append(w)
            else:
                # The current word can be added to the last line.
                lines[-1] = new_line
        return lines
    except IndexError:
        return [""]

def show_main_menu(paused = False):
    '''shows main menue. Allows options to be actuated'''
    screen = pygame.display.get_surface()
    splashImage = singleton_image_cache.get("splash.png")
    screen.blit(splashImage, (0,0))

    # Update the display
    pygame.display.flip()
    # Freeze until a key is pressed
    proceed = False
    while not proceed:
        # If the user hit one of the inputs, proceed
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                key = event.unicode
                if key == 'i':
                    draw_instructions(paused)
                elif key == 's':
                    from level import goto_level
                    goto_level(0)
                    proceed = True
                elif key == 'q':
                    pygame.quit()
                    sys.exit()
                
                
        time.sleep(0.02) # avoid hogging the CPU

def draw_instructions(paused = False):

    '''draws a visual guide to the game'''
    width_msg_offset = width_msg * 3 / 4
    PAD = 30
    screen = pygame.display.get_surface()
    image_farm = singleton_image_cache.get("farm.png")
    image_house = singleton_image_cache.get("house.png")
    house_msg = "This is a house. You need houses for workers"
    house_msg += " to live in or else no one will come to"
    house_msg += " your city. 10 workers can live in each house."
    farm_msg = "This is a farm. Farms grow food for your workers"
    farm_msg += " to eat. Assign workers here to gather food."
    lines = word_wrap(farm_msg, width_msg_offset, font_msg)
    farm_height = font_msg.get_height() * len(lines)
    lines.append("")
    lines.extend(word_wrap(house_msg, width_msg_offset, font_msg))
    house_height = font_msg.get_height() * len(lines)
    lines.append("")
    lines.extend(word_wrap("Press any key to continue", width_msg_offset, font_msg))

    # Render each line with a dark gray color
    lines = [font_msg.render(l, True, (50, 50, 50)) for l in lines]
    
    # The height of the message is the sum of the heights of each line
    tot_height = sum([l.get_height() for l in lines])

    x1 = screen.get_width()/2 - width_msg/2 # left edge of the box
    y1 = screen.get_height()/2 - tot_height/2   # starting y coord
    x2 = screen.get_width()/2 - width_msg_offset/2 + PAD
    PAD = 30
    # Draw background box
    pygame.draw.rect(screen, (240, 240, 240), (x1 - PAD, y1 - PAD, width_msg + 2*PAD, tot_height + 2*PAD))
    pygame.draw.rect(screen, (50, 50, 50), (x1 - PAD, y1 - PAD, width_msg + 2*PAD, tot_height + 2*PAD), 4)
    
    y = y1
    for line in lines:
        screen.blit(line, (x2, y))
        y += line.get_height()

    screen.blit(image_farm, (x1, y1 + (farm_height - image_farm.get_height())/2))
    height_diff = house_height - farm_height
    screen.blit(image_house, (x1, y1 + farm_height + (height_diff - image_house.get_height())/2))

    # Update the displayi
    pygame.display.flip()

    # Freeze until a key is pressed
    proceed = False
    while not proceed:
        # If the user hit any key, proceed
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                proceed = True
        time.sleep(0.01) # avoid hogging the CPU
    if not paused:
        splashImage = singleton_image_cache.get("splash.png")
        screen.blit(splashImage, (0,0))
    else:
        new_render()
    proceed = False
    ## The second screen starts here
    image_mine = singleton_image_cache.get("mine.png")  
    image_stream = singleton_image_cache.get("stream.png")
    image_tree = singleton_image_cache.get("tree.png")    
    
    mine_msg = "This is a mine. Assign workers here to gather gold."
    stream_msg = "This is a stream. Workers can gather gold from here too, but not quite as quickly."
    tree_msg = "This is a forest. Workers can gather wood here."
    lines = word_wrap(mine_msg, width_msg_offset, font_msg)
    mine_height = font_msg.get_height() * len(lines)
    lines.append("")
    lines.extend(word_wrap(stream_msg, width_msg_offset, font_msg))
    stream_height = font_msg.get_height() * len(lines)
    lines.append("")
    lines.extend(word_wrap(tree_msg, width_msg_offset, font_msg))
    tree_height = font_msg.get_height() * len(lines)
    lines.append("")
    lines.extend(word_wrap("Press any key to continue", width_msg_offset, font_msg))
    lines = [font_msg.render(l, True, (50, 50, 50)) for l in lines]
    
    # The height of the message is the sum of the heights of each line
    tot_height = sum([l.get_height() for l in lines])
    y1 = screen.get_height()/2 - tot_height/2   # starting y coord

    # Draw background box
    pygame.draw.rect(screen, (240, 240, 240), (x1 - PAD, y1 - PAD, width_msg + 2*PAD, tot_height + 2*PAD))
    pygame.draw.rect(screen, (50, 50, 50), (x1 - PAD, y1 - PAD, width_msg + 2*PAD, tot_height + 2*PAD), 4)
    
    y = y1
    for line in lines:
        screen.blit(line, (x2, y))
        y += line.get_height()
        
    screen.blit(image_mine, (x1, y1 + (mine_height - image_mine.get_height())/2) )
    height_diff = stream_height - mine_height
    screen.blit(image_stream, (x1, y1 + mine_height + (height_diff - image_stream.get_height())/2))
    height_diff = tree_height - stream_height
    screen.blit(image_tree, (x1, y1 + stream_height + (height_diff - image_tree.get_height())/2))
    pygame.display.flip()

    while not proceed:
        # If the user hit any key, proceed
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                proceed = True
        time.sleep(0.01) # avoid hogging the CPU
    if not paused:
        screen.blit(splashImage, (0,0))
    else:
        new_render()
            
    # The third Screen starts here
    proceed = False
    image_grave = singleton_image_cache.get("grave.png") 
    grave_msg = "This is a cemetery. If your workers die then these will start popping up. They can't"
    grave_msg += " be destroyed and take up valuable real estate, so be careful!"
    lines = word_wrap(grave_msg, width_msg_offset, font_msg)
    lines.append("")
    lines.extend(word_wrap("Press any key to continue", width_msg_offset, font_msg))
    lines = [font_msg.render(l, True, (50, 50, 50)) for l in lines]
    tot_height = sum([l.get_height() for l in lines])
    y1 = screen.get_height()/2 - tot_height/2   # starting y coord
    pygame.draw.rect(screen, (240, 240, 240), (x1 - PAD, y1 - PAD, width_msg + 2*PAD, tot_height + 2*PAD))
    pygame.draw.rect(screen, (50, 50, 50), (x1 - PAD, y1 - PAD, width_msg + 2*PAD, tot_height + 2*PAD), 4)
    y = y1
    for line in lines:
        screen.blit(line, (x2, y))
        y += line.get_height()
    screen.blit(image_grave, (x1, y1 + tot_height/2 - (image_mine.get_height())/2))
    pygame.display.flip()
    while not proceed:
        # If the user hit any key, proceed
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                proceed = True
        time.sleep(0.01) # avoid hogging the CPU
    if not paused:
        show_main_menu() 
    else:
        new_render()
        show_pause_menu()   
    
def show_message(msg):
    '''Show an important message. The game will be paused until the player
    presses a key to acknowledge the message. If msg is something other than
    a string, it will be converted to a string.'''
    msg = str(msg)
    screen = pygame.display.get_surface()

    # Unit tests are run in headless mode, i.e., there is no display. In this
    # case, we don't actually want to display messages.
    if screen is None:
        return

    lines = word_wrap(msg, width_msg, font_msg)
    lines.append('')
    lines.append('Press any key to continue...')

    # Render each line with a dark gray color
    lines = [font_msg.render(l, True, (50, 50, 50)) for l in lines]
    # The height of the message is the sum of the heights of each line
    height = sum([l.get_height() for l in lines])

    x1 = screen.get_width()/2 - width_msg/2
    y1 = screen.get_height()/2 - height/2
    PAD = 30

    # Draw background box
    pygame.draw.rect(screen, (240, 240, 240), (x1 - PAD, y1 - PAD, width_msg + 2*PAD, height + 2*PAD))
    pygame.draw.rect(screen, (50, 50, 50), (x1 - PAD, y1 - PAD, width_msg + 2*PAD, height + 2*PAD), 4)

    # Draw each line of text
    y = y1
    for line in lines:
        screen.blit(line, (x1, y))
        y += line.get_height()

    # Update the display
    pygame.display.flip()

    # Freeze until a key is pressed
    proceed = False
    while not proceed:
        # If the user hit any key, proceed
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                proceed = True
        time.sleep(0.01) # avoid hogging the CPU

def get_input(msg):
    """Show a message and prompts the user to input a string. Returns the
    string entered by the user."""
    msg = str(msg)
    screen = pygame.display.get_surface()

    # Unit tests are run in headless mode, i.e., there is no display. In this
    # case, we don't actually want to display messages.
    if screen is None:
        return

    lines = word_wrap(msg, width_msg, font_msg)
    lines.append('') # a blank line for padding, and then...
    lines.append('') # the last line will show what the user has typed

    # Render each line with a dark gray color
    lines = [font_msg.render(l, True, (50, 50, 50)) for l in lines]
    # The height of the message is the sum of the heights of each line
    height = sum([l.get_height() for l in lines])

    x1 = screen.get_width()/2 - width_msg/2
    y1 = screen.get_height()/2 - height/2
    PAD = 30

    user_input = ""
    proceed = False
    while not proceed:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                # If the user hit enter, we're done
                if event.key == K_RETURN:
                    proceed = True
                # If the user hits backspace, delete a character from user_input
                elif event.key == K_BACKSPACE:
                    if len(user_input) > 0:
                        user_input = user_input[:-1]
                # If the user typed a printable character, add it to user_input
                else:
                    if event.unicode != '':
                        user_input = user_input + event.unicode

        # cursor will alternate between "|" (on) and "" (off) based on time
        cursor = "|" if (time.time() % 1 > 0.5) else ""
        # The last line is the user's input plus the cursor
        lines[-1] = font_msg.render(user_input + cursor, True, (50, 50, 50))

        # Draw background box
        pygame.draw.rect(screen, (240, 240, 240), (x1 - PAD, y1 - PAD, width_msg + 2*PAD, height + 2*PAD))
        pygame.draw.rect(screen, (50, 50, 50), (x1 - PAD, y1 - PAD, width_msg + 2*PAD, height + 2*PAD), 4)

        # Draw each line of text
        y = y1
        for line in lines:
            screen.blit(line, (x1, y))
            y += line.get_height()

        # Update the display
        pygame.display.flip()
        time.sleep(0.01) # avoid hogging the CPU

    return user_input


current_warning = "Without food, your workers will starve. Start by building " \
                + "farms and placing workers on them."

def show_warning(warning):
    """
    Present the user with a warning, which will be displayed in the corner
    of the screen. This will replace whatever the previous warning was, and it
    will persist until show_warning is called again with a different warning.
    """
    global current_warning
    current_warning = warning


def render_warning():
    """Paint the most recent warning to the screen."""
    screen = pygame.display.get_surface()

    # Split the warning into separate lines
    lines = word_wrap(current_warning, width_warning, font_warning)

    # Render each line using a dark gray color
    lines = [font_warning.render(l, True, (50, 50, 50)) for l in lines]

    # The top-left corner of the warning box
    X_0, Y_0 = 620, 400

    # Blit each line to the screen
    y = Y_0
    for line in lines:
        screen.blit(line, (X_0, y))
        y += line.get_height()

def show_pause_menu():
    ''' Show pause menu to the user'''
    from interface import singleton_interface
    screen = pygame.display.get_surface()
    #pygame.set_cursor(NORMAL)
    pygame.mouse.set_cursor(default_cursor[0],default_cursor[1],default_cursor[2],default_cursor[3])
    pygame.mouse.set_visible(True)
    new_render(False)
    lines = ["Pause Menu", "", "Press C to Continue", "Press R to Restart this level"]
    lines.extend(["Press I for Instructions"])
    lines.extend(["Press S to Save game", "Press L to Load game", "Press M for Main Menu "])
    
    # Render each line with a dark gray color
    lines = [font_msg.render(l, True, (50, 50, 50)) for l in lines]
    # The height of the message is the sum of the heights of each line
    height = sum([l.get_height() for l in lines])

    x1 = screen.get_width()/2 - width_msg/2
    y1 = screen.get_height()/2 - height/2
    PAD = 30

    # Draw background box
    pygame.draw.rect(screen, (240, 240, 240), (x1 - PAD, y1 - PAD, width_msg + 2*PAD, height + 2*PAD))
    pygame.draw.rect(screen, (50, 50, 50), (x1 - PAD, y1 - PAD, width_msg + 2*PAD, height + 2*PAD), 4)
    
    y = y1
    for line in lines:
        screen.blit(line, (x1, y))
        y += line.get_height()

    # Update the display
    pygame.display.flip()
    # Freeze until a key is pressed
    proceed = False
    while not proceed:
        # If the user hit one of the inputs, proceed
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                key = event.unicode
                if key == 'i':
                    draw_instructions(True)
                    proceed = True
                elif key == 'c':
                    proceed = True
                elif key == 'r':
                    from level import levels, current_level
                    levels[current_level].begin()
                    proceed= True
                elif key == 's':
                    save_game()
                    show_pause_menu()
                    proceed = True
                elif key == 'l':
                    load_game()
                    proceed = True
                elif key == 'm':
                    show_main_menu(True)
                    proceed = True
                    
                
                
        time.sleep(0.02) # avoid hogging the CPU
    pygame.mouse.set_visible(False)
    new_render()
    
    
def save_game():
    from level import levels, current_level
    name = get_input("What should this saved game be called? (You may want to use your first name.)")
    if name.strip() == '':
        return
    path = get_save_path(name)
    with open(path, 'w') as f:
        f.write(str(current_level))
        f.close()

def get_save_path(name):
    '''Convert a save name into a proper file path'''
    return 'saves/' + name + '.sav'
    
def load_game():
    from level import goto_level
    name = get_input("Enter the name of the saved game.")
    if name.strip() == '':
        return
    path = get_save_path(name)
    try:
        with open(path, 'r') as f:
            saved_level = int(f.read())
            goto_level(saved_level)
    except IOError:
        show_message("No save file with that name was found.")

def new_render(flag= True):
    ''' Tells everything to repaint themselves'''
    from grid import singleton_grid
    from interface import singleton_interface
    # Paint he background
    screen = pygame.display.get_surface()
    screen.fill(bg_color)

    # Paint the grid
    singleton_grid.paint()

    # Paint the buttons, resources, etc.
    singleton_interface.paint(flag)

    # Update the display
    pygame.display.flip()
