# This py file contains all of my Game's Global variables.
# NOTICE - Changing any of the variables' values here will cause changes in the game itself

import os

# General Information
__author__ = "Dolev Raziel"
__email__ = "dolev.raziel@gmail.com"
__contact__ = "Phone: +972545335441"
__copyright__ = "Copyright 2019, Dolev Raziel"
__game_name__ = "ULTIMATE SOCCER 2K19"
__version__ = "1.0.0"
__status__ = "Prototype"

# Colors
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
MID_GRAY = (30, 30, 30)
MID_WHITE = (233, 233, 233)
PINK = (222, 17, 102)

# Login Menu Vars



# Special Vars
# Special vars are usually vars that keep repeating and showing up in the code

game_time = 20


window_width = 1266  # px
window_height = 520  # px
database = os.getcwd() + r'/login/game_database_{}.db'.format(os.environ.get('USERNAME'))


single_player_message = 'Welcome to the groups selection menu. ' \
                        'Select your groups and kits and press Enter when both sides are ready to play.' \
                        'The Home Player will navigate the menu and play the game using the WASD keys.' \
                        'The Away Player will navigate the menu and play the game using the arrow keys.'


