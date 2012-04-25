'''
Placing commonly used constants in a separate file helps avoid problems with
circular imports. Also, since this module has no dependencies and never will,
we can use "from constants import *" without worrying about importing things
we don't want.
'''

# These are the interface modes. Modes are usually set by clicking a button
# like "build house". See interface.py and button.py.
NORMAL,           \
BUILD_HOUSE,      \
BUILD_FARM,       \
BUILD_MINE,       \
DESTROY_BUILDING, \
ASSIGN_WORKER,    \
REMOVE_WORKER     \
= range(7)

# RGB tuples for some common colors.
WHITE  = (255,255,255)
YELLOW = (255, 250, 150)
GREY   = (100, 100, 100)
GREEN  = (0x66, 0xFF, 0x99)
RED    = (0xFF, 0x66, 0x66)
BLUE   = (0x33, 0x99, 0xFF)
BROWN  = (0x99, 0x66, 0x33)

