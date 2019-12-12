import pygame
import os
import sys
import pymsgbox  # for message boxes
from tkinter.simpledialog import *

from pygame.locals import *

import GameVariables

user = sys.argv[1]
path = os.getcwd() + r'\new_menu\SINGLEPLAYER'
gameDisplay = pygame.display.set_mode((GameVariables.window_width, GameVariables.window_height))


def create_dictionary(player):  # the function recieves a string ("home" or "away") and returns a dictionary with the images
    dictionary = {}
    i = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            filename = os.path.join(root, file)
            if filename.endswith('.jpg') and player in filename:
                i += 1
                dictionary[i] = filename
    return dictionary


home_dictionary = create_dictionary("HOME")
away_dictionary = create_dictionary("AWAY")
home_currently_viewing = 2
away_currently_viewing = 3


def SinglePlayerMenuInit():  # initializes pygame and pygame.mixer
    pygame.init()
    pygame.display.set_caption('Single Player - Select Teams')  # screen title
    return


def startingMenu():
    global home_currently_viewing
    global away_currently_viewing

    myfont = pygame.font.SysFont("SecularOne-Regular", 48)
    pygame.mouse.set_visible(0)  # disables the mouse cursor while being in the main screen.


    #self.FPS = 60
    #self.CLOCK = pygame.time.Clock()

    home_background = pygame.image.load(home_dictionary.get(home_currently_viewing))
    away_background = pygame.image.load(away_dictionary.get(away_currently_viewing))
    stripe = pygame.image.load(path + r'\STRIPE.jpg')
    gameDisplay.blit(home_background, (0, 0))  # drawing the background
    gameDisplay.blit(stripe, (623, 0))  # drawing the background
    gameDisplay.blit(away_background, (644, 0))  # drawing the background

    home_user = myfont.render(user, 1, GameVariables.MID_GRAY)
    away_user = myfont.render("Guest", 1, GameVariables.MID_WHITE)
    gameDisplay.blit(home_user, (91, 75))
    gameDisplay.blit(away_user, (746, 75))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.display.quit()  # Quit pygame if window in closed
            os.system(f"python MainMenu2.py {user}")
            sys.exit()

        if event.type == pygame.KEYDOWN:  # if key pressed
            if event.key == pygame.K_d:
                if home_currently_viewing != 8:
                    home_currently_viewing += 1

            if event.key == pygame.K_a:
                if home_currently_viewing != 1:
                    home_currently_viewing -= 1

            if event.key == pygame.K_w:
                if home_currently_viewing in range(5, 9):
                    home_currently_viewing -= 4

            if event.key == pygame.K_s:
                if home_currently_viewing in range(1, 5):
                    home_currently_viewing += 4

            if event.key == pygame.K_UP:
                if away_currently_viewing in range(5, 9):
                    away_currently_viewing -= 4

            if event.key == pygame.K_DOWN:
                if away_currently_viewing in range(1, 5):
                    away_currently_viewing += 4

            if event.key == pygame.K_RIGHT:
                if away_currently_viewing != 8:
                    away_currently_viewing += 1

            if event.key == pygame.K_LEFT:
                if away_currently_viewing != 1:
                    away_currently_viewing -= 1

            if event.key == pygame.K_RETURN:
                pygame.display.quit()
                # when starting the game, we will send 6 args
                # in this order: player1_name, player1_selected_skin, player2_name, player2_selected_skin
                game_time = pymsgbox.prompt('How many minutes would you like to play?', default='type a number between 1 to 90')
                while int(game_time) not in range(1, 91):
                    game_time = pymsgbox.prompt('How many minutes would you like to play?', default='type a number between 1 to 90')
                if pymsgbox.confirm('Would you like your game to be broadcasted?', 'Broadcasting', ["Yes", 'No']) == 'Yes':
                    broadcast_game = True
                else: broadcast_game = False
                GameVariables.game_time = game_time
                os.system(f'python MyGAME.py {user} {home_currently_viewing} Guest {away_currently_viewing} {broadcast_game}')
                sys.exit()


def update_screen(background):
    background = pygame.image.load(background)
    gameDisplay.blit(background, (0, 0))  # drawing the background


def main():
    SinglePlayerMenuInit()  # will create the basic environment for the game
    pymsgbox.alert(GameVariables.single_player_message)
    while True:
        startingMenu()
        pygame.display.update()

if __name__ == "__main__":
    main()