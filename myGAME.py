import math
import sys
import os

from requests import get
import socket
import sqlite3

import pygame  # the best lib in python
from pygame.locals import *
from Utilities import SoccerBall  # our soccerball Class
from Utilities import ScoreBoard  # our ScoresBoard Class
from Utilities import FriendlyPlayer  # our ScoresBoard Class
from Utilities import EnemyPlayer  # our ScoresBoard Class
from random import randint
import asyncio

import GameVariables
updated = False

# --------------------- # lets define some goal sounds
path = os.getcwd() + r'\audio'
sound = path + "\\" + "(PSG) PARIS GOAL SONG.mp3"
sound2 = path + "\\" + "Austria Wien Goal.mp3"
sound3 = path + "\\" + "napoli.mp3"
sound4 = path + "\\" + "OFFICIAL UEFA EURO 2016 GOAL SONG - Seven Nation Army Remix.mp3"
sound5 = path + "\\" + "WOLVERHAMPTON GOAL SONG.mp3"
special_6_2 = path + "\\" + "יש טרבל הפועל באר שבע - מכבי תל אביב 62 תקציר גמר הגביע! 20.5.15.mp3"
special_6_1 = path + "\\" + "נדב יעקבי - לא היה כדבר הזה (צלצול).mp3"
goal_songs = [sound, sound2, sound3, sound4, sound5]


kit_Chelsea = os.getcwd() + r'\skins\chlesea10.png'
kit_Barcelona = os.getcwd() + r'\skins\barcelona10.png'
kit_Liverpool = os.getcwd() + r'\skins\liverpool9.png'
kit_Juventus = os.getcwd() + r'\skins\jeventus7.png'
kit_RealMadrid = os.getcwd() + r'\skins\realmadrid11.png'
kit_ManUnited = os.getcwd() + r'\skins\united.png'
kit_InterMilan = os.getcwd() + r'\skins\inter.png'
kit_Bayern = os.getcwd() + r'\skins\bayern.png'

kits_dictionary = {1: kit_Chelsea,
                   2: kit_Barcelona,
                   3: kit_RealMadrid,
                   4: kit_Juventus,
                   5: kit_ManUnited,
                   6: kit_InterMilan,
                   7: kit_Liverpool,
                   8: kit_Bayern}

# ---------------- SQL VARS
connection = None
sql_cursor = None
# ----------------

def connect_to_socket(port):
    host = '0.0.0.0'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(1)

    conn, ip_adress = s.accept()
    print('Connected by', ip_adress)
    return


class Game:
    def __init__(self):
        self.GAME_NAME = f"{GameVariables.__game_name__} - {GameVariables.__author__}"
        self.W = 1750
        self.H = 1000
        # -------
        self.FPS = 50
        self.CLOCK = pygame.time.Clock()
        # -------
        self.background = os.getcwd() + r'\championsleague\court1.jpg'  # the background
        self.background = pygame.image.load(self.background)
        self.background = pygame.transform.smoothscale(self.background, (self.W, self.H))
        # ---------------------------------------------------------------------------------------------
        pygame.init()
        pygame.mixer.init()
        self.DS = pygame.display.set_mode((self.W, self.H))
        pygame.display.set_caption(self.GAME_NAME)
        # ----------------------------------------------------------------------------------------------
        self.frdPlayer = FriendlyPlayer(1005, (self.H/2) - 40, kits_dictionary[int(sys.argv[4])])
        self.enmPlayer = EnemyPlayer(495 - 2 * 40, (self.H/2) - 40, kits_dictionary[int(sys.argv[2])])
        self.player_List = [self.frdPlayer, self.enmPlayer]
        self.ball = SoccerBall((self.W/2) - 1.7 * 19, (self.H/2) - 2 * 19)
        self.scoreBoard = ScoreBoard()
        if sys.argv[5]:
            self.public_ip = get('https://api.ipify.org').text
            self.local_ip = socket.gethostbyname(socket.gethostname())
            self.port = randint(2000, 10001)
            #connect_to_socket(self.port)
        # ----------------------------------------------------------------------------------------------

    def events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:  #i will fix it later. [pause screen]
                pass
        return

    def show_results_to_players_and_quit(self, string):
        if 'DRAW!' in string:
            image = os.getcwd() + r'\new_menu\GAME\draw.png'
        else:
            image = os.getcwd() + r'\new_menu\GAME\win.png'
        image_to_print = pygame.image.load(image)

        font = pygame.font.Font(None, 64)
        string_to_print = font.render(string, True, (255, 255, 255))
        self.DS.blit(image_to_print, ((self.W / 2) - 313, (self.H/2) - 338))
        self.DS.blit(string_to_print, ((self.W/2-300), self.H/2+100))
        return

    def results(self):
        global updated

        if self.scoreBoard.enemyteam.goals > self.scoreBoard.myteam.goals:
            win = True
            string = f'{sys.argv[1]} WON THE MATCH!'
        elif self.scoreBoard.enemyteam.goals < self.scoreBoard.myteam.goals:
            win = False
            string = 'GUEST WON THE MATCH!'
        else:
            win = False
            string = 'ITS A DRAW!'

        if self.scoreBoard.myteam.goals == 0:
            clean_sheet = True
            conceded = 0
        else:
            clean_sheet = False
            conceded = self.scoreBoard.myteam.goals
        goals = self.scoreBoard.enemyteam.goals

        if not updated:
            global connection
            global sql_cursor
            connection = sqlite3.connect(GameVariables.database)
            sql_cursor = connection.cursor()

            sql_cursor.execute(f"""UPDATE users
                                   SET played = played + 1, 
                                   wins = wins + {1 if win else 0}, 
                                   losses = losses + {1 if not win else 0}, 
                                   goals = goals + {goals},
                                   conceded = conceded + {conceded},
                                   clean_sheets = clean_sheets + {1 if clean_sheet else 0}
                                   WHERE username = '{sys.argv[1]}';""")
            connection.commit()
            print("added to database")
            updated = True
        self.show_results_to_players_and_quit(string)
        return

    def game_ended(self):
        for i in self.player_List:
            i.allow_players_movement = False
            i.shoot = False
        rect = pygame.Surface((self.W, self.H), pygame.SRCALPHA, 32)
        rect.fill((0, 0, 0, 70))
        self.DS.blit(rect, (0, 0))
        #fade = pygame.Surface((self.W, self.H))
        #fade.fill((0, 0, 0))
        #for alpha in range(0, 10):
            #fade.set_alpha(alpha)
            #self.DS.blit(fade, (0, 0))
            #pygame.time.delay(5)
        return

    def check_collision_players(self):  # the function checks if there is a collision between the players (analitit)
        x1, y1, radius = self.frdPlayer.x, self.frdPlayer.y, self.frdPlayer.radius
        x2, y2, radius2 = self.enmPlayer.x, self.enmPlayer.y, self.enmPlayer.radius
        distance = math.hypot(x1 - x2, y1 - y2)
        if distance <= radius + radius2:
            self.frdPlayer.xVelocity /= -1
            self.frdPlayer.yVelocity /= -1
            self.enmPlayer.xVelocity /= -1
            self.enmPlayer.yVelocity /= -1
        return

    def check_collision_with_ball(self):  # the function checks if there is a collision between the players and the ball (analitit)
        for any_player in self.player_List:  #checks every player from the list
            x1, y1, radius = any_player.x, any_player.y, any_player.radius
            x2, y2, radius2 = self.ball.x, self.ball.y, self.ball.radius
            distance = math.hypot(x1 - x2, y1 - y2)
            if distance <= radius + radius2:
                if any_player.x < self.ball.x:
                    if any_player.shoot:
                        if any_player.xVelocity != 0: self.ball.xVelocity = any_player.xVelocity + 5
                        if any_player.yVelocity != 0: self.ball.yVelocity = any_player.yVelocity + 5
                    else:
                        if any_player.xVelocity != 0: self.ball.xVelocity = any_player.xVelocity + 1
                        if any_player.yVelocity != 0: self.ball.yVelocity = any_player.yVelocity + 1
                if any_player.x > self.ball.x:
                    if any_player.shoot:
                        if any_player.xVelocity != 0: self.ball.xVelocity = any_player.xVelocity -5
                        if any_player.yVelocity != 0: self.ball.yVelocity = any_player.yVelocity -5
                    else:
                        if any_player.xVelocity != 0: self.ball.xVelocity = any_player.xVelocity -1
                        if any_player.yVelocity != 0: self.ball.yVelocity = any_player.yVelocity -1
        return

    def check_goal(self, finished):

        if self.ball.inGoalLeft or self.ball.inGoalRight:
            if not finished:
                if self.ball.inGoalLeft:
                    self.scoreBoard.myteam.one_more()
                if self.ball.inGoalRight:
                    self.scoreBoard.enemyteam.one_more()

                one_six = self.scoreBoard.enemyteam.goals == 6 and self.scoreBoard.myteam.goals == 1
                six_one = self.scoreBoard.enemyteam.goals == 1 and self.scoreBoard.myteam.goals == 6
                two_six = self.scoreBoard.enemyteam.goals == 6 and self.scoreBoard.myteam.goals == 2
                six_two = self.scoreBoard.enemyteam.goals == 2 and self.scoreBoard.myteam.goals == 6

                if two_six or six_two:
                    pygame.mixer.music.load(special_6_2)
                elif one_six or six_one:
                    pygame.mixer.music.load(special_6_1)
                elif not two_six or not six_two or not six_one or not one_six:
                    pygame.mixer.music.load(goal_songs[randint(0, len(goal_songs) - 1)])
                pygame.mixer.music.play()

            self.ball.inGoalRight = not self.ball.inGoalRight
            self.ball.inGoalLeft = not self.ball.inGoalLeft
            self.ball.x = self.W/2 - 1.7 * self.ball.radius
            self.ball.y = self.H/2 - 2 * self.ball.radius
            self.ball.xVelocity = 0
            self.ball.yVelocity = 0
        return

    def print_connection_details(self):
        font = pygame.font.Font(None, 24)
        public_ip = font.render(f'PUBLIC IP: {self.public_ip}', True, (255, 255, 0))
        local_ip = font.render(f'LOCAL IP: {self.local_ip}', True, (255, 255, 0))
        port = font.render(f'PORT: {self.port}/UDP', True, (255, 255, 0))

        self.DS.blit(public_ip, (2, 2))
        self.DS.blit(local_ip, (2, 20))
        self.DS.blit(port, (2, 40))
        return

    def run(self):  # this function starts the whole game process
        self.events()
        finished = self.scoreBoard.time.minutes * 60 + self.scoreBoard.time.seconds > GameVariables.game_time
        self.DS.blit(self.background, (0, 0))  # drawing the background
        self.ball.do()  # call the ball
        for i in self.player_List:
            i.do()  # call the players
        self.check_collision_players()  # check the collision
        self.check_collision_with_ball()  # check the collision
        self.check_goal(finished)
        self.scoreBoard.draw(finished)  # draw the scoreboard

        #self.CLOCK.tick(self.FPS)  # ticking the clock (how many frames per sec)

        if finished:
            self.game_ended()
            self.results()

        if sys.argv[5]:
            self.print_connection_details()
        pygame.display.update()  # update the display (pygame lib method)
        return


def main():
    my_game = Game()  # the game is actually a class, so lets define it :)
    # when starting the game, we will receive 4 args from the single player menu
    # in this order: player1_name, player1_selected_skin, player2_name, player2_selected_skin

    my_game.scoreBoard.enemyteam.name = sys.argv[1]
    my_game.scoreBoard.myteam.name = sys.argv[3]

    while True:  # temporary only. soon there will be a menu
        my_game.run()  # calls the main function from the Game class.



if __name__ == "__main__":
    main()








