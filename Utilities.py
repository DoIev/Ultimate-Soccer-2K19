import pygame
import os, sys
from pygame.locals import *
import math
import time

import GameVariables
#  ----------------------

friction = 0.03

W, H = 1750, 1000

behind_net_margin = 60

top_border_for_players = 100
left_border_for_players = 0
right_border_for_players = W
bottom_border_for_players = 845

top_border_for_ball = 126
left_border_for_ball = 128
right_border_for_ball = W - 128
bottom_border_for_ball = 820

gate_top_corner_y = 403
gate_bottom_corner_y = 544

DS = pygame.display.set_mode((W, H))
# ----------------


checkfor1secdelay1 = time.time()


class ScoreBoard:
    def __init__(self):
        self.time = OnTheClock()
        self.enemyteam = EnemyTeam()
        self.myteam = MyTeam()
        self.image = os.getcwd() + r'\championsleague\output-onlinejpgtools.png'
        self.scoreboard = pygame.image.load(self.image).convert_alpha()
        self.x = (W/2) - 315
        self.y = 30

    def draw(self, finished):
        # --------------------drawing the scoreboard
        DS.blit(self.scoreboard, (self.x, self.y))

        # --------------------drawing the teams
        myfont = pygame.font.SysFont("Trebuchet MS", 30)

        labelTEAM1 = myfont.render(self.myteam.name, 1, GameVariables.WHITE)
        labelTEAM1goals = myfont.render(str(self.myteam.goals), 1, GameVariables.WHITE)
        labelTEAM2 = myfont.render(self.enemyteam.name, 1, GameVariables.WHITE)
        labelTEAM2goals = myfont.render(str(self.enemyteam.goals), 1, GameVariables.WHITE)
        DS.blit(labelTEAM1, (830 + 128, self.y + 5))
        DS.blit(labelTEAM2, (520 + 128, self.y + 5))
        DS.blit(labelTEAM1goals, (756 + 128, self.y + 5))
        DS.blit(labelTEAM2goals, (720 + 128, self.y + 5))
        # --------------------drawing the clock
        myfont2 = pygame.font.SysFont("Trebuchet MS", 24)
        pygame.draw.rect(DS, GameVariables.WHITE, [696 + 128, self.y + 45, 100, 30])  # x then y then width then height
        if not finished:
            stopwatch = myfont2.render(self.update_clock(), 1, GameVariables.BLACK)
            DS.blit(stopwatch, (720 + 128, self.y + 45 + 1))
        else:
            stopwatch = myfont2.render("FT", 1, GameVariables.BLACK)
            DS.blit(stopwatch, (720 + 128+15, self.y + 45 + 1))


    def update_clock(self):
        global checkfor1secdelay1
        checkfor1secdelay2 = time.time()
        if checkfor1secdelay2 - checkfor1secdelay1 >= 1:
            self.time.one_more()
            checkfor1secdelay1 = time.time()
        return self.time.get_time()


class OnTheClock:
    def __init__(self):
            self.seconds = 0
            self.minutes = 0

    def one_more(self):
        if self.seconds == 59:
            self.seconds = 0
            self.minutes += 1
        else:
            self.seconds += 1
        return

    def get_time(self):
        if self.minutes < 10:
            minutes_to_print = '0' + str(self.minutes)
        else:
            minutes_to_print = self.minutes
        if self.seconds < 10:
            seconds_to_print = '0' + str(self.seconds)
        else:
            seconds_to_print = self.seconds

        return f'{minutes_to_print}:{seconds_to_print}'


class MyTeam:
    def __init__(self):
        self.goals = 0
        self.name = ""

    def one_more(self):
        self.goals += 1


class EnemyTeam:
    def __init__(self):
        self.goals = 0
        self.name = ""

    def one_more(self):
        self.goals += 1

# --------------------------------------------------------------------------


class Player:
    def __init__(self, x, y):

        self.radius = 40
        self.x = x #+ self.radius
        self.y = y #+ self.radius
        self.xVelocity = 0
        self.yVelocity = 0
        self.angle = 0
        self.shoot = False
        self.allow_players_movement = True

    def move(self):
        if self.xVelocity > 0: self.xVelocity -= friction
        if self.xVelocity < 0: self.xVelocity += friction
        if self.yVelocity > 0: self.yVelocity -= friction
        if self.yVelocity < 0: self.yVelocity += friction
        if self.xVelocity != 0: self.angle = math.degrees(math.atan(self.yVelocity/self.xVelocity))
        elif self.xVelocity == 0: self.angle = "/"
        if self.yVelocity > -0.01 and self.yVelocity < 0.1: self.yVelocity = 0
        if self.xVelocity > -0.01 and self.xVelocity < 0.1: self.xVelocity = 0

        if right_border_for_players - int(self.x) <= 2*self.radius:
            self.xVelocity = -self.xVelocity
        if abs(left_border_for_players - int(self.x)) <= 5:  # 5 - margin of error
            self.xVelocity = -self.xVelocity
        if bottom_border_for_players - int(self.y) <= 2*self.radius:
            self.yVelocity = -self.yVelocity
        if int(self.y) - top_border_for_players <= 5:
            self.yVelocity = -self.yVelocity

        self.x += self.xVelocity
        self.y += self.yVelocity

    def draw(self):
        DS.blit(self.skin, (self.x, self.y))
        if sys.argv[1] == 'Admin':
            myfont = pygame.font.SysFont("Trebuchet MS", 12)

            if self.shoot:
                color = GameVariables.RED
            else:
                color = GameVariables.YELLOW

            angleToPrint = myfont.render(str(self.angle)[0:5] + " degrees", 1, color)
            velocityToPrint = myfont.render(str(math.sqrt(pow((self.xVelocity), 2) + pow((self.yVelocity), 2)))[0:5], 1,color)
            DS.blit(angleToPrint, (self.x, self.y + 80))
            DS.blit(velocityToPrint, (self.x, self.y + 90))

    def keys(self):
        pass

    def do(self):
        self.keys()
        self.move()
        self.draw()


class FriendlyPlayer(Player):
    def __init__(self, x, y, image):
        Player.__init__(self, x, y)
        self.image = image
        self.skin = pygame.image.load(self.image).convert_alpha()
        self.skin = pygame.transform.smoothscale(self.skin, (80, 80))
        self.rect = self.skin.get_rect()
        # pygame.draw.circle(self.skin, YELLOW, self.rect.center, self.radius)

    def keys(self):
        if self.allow_players_movement:
            k = pygame.key.get_pressed()
            self.shoot = False

            if k[K_RIGHT] or k[K_6]:
                if self.xVelocity < 5:
                    self.xVelocity = self.xVelocity + 0.5
            if k[K_LEFT] or k[K_4]:
                if self.xVelocity > -5:
                    self.xVelocity = self.xVelocity - 0.5
            if k[K_UP] or k[K_8]:
                if self.yVelocity > -5:
                    self.yVelocity = self.yVelocity - 0.5
            if k[K_DOWN] or k[K_5]:
                if self.yVelocity < 5:
                    self.yVelocity = self.yVelocity + 0.5
            if k[K_KP_ENTER] or k[K_KP0]:
                self.shoot = True


class EnemyPlayer(Player):
    def __init__(self, x, y, image):
        Player.__init__(self, x, y)
        self.image = image
        self.skin = pygame.image.load(self.image).convert_alpha()
        self.skin = pygame.transform.smoothscale(self.skin, (80, 80))
        self.rect = self.skin.get_rect()
        # pygame.draw.circle(self.skin, YELLOW, self.rect.center, self.radius)

    def keys(self):
        if self.allow_players_movement:
            k = pygame.key.get_pressed()
            self.shoot = False

            if k[K_d]:
                if self.xVelocity < 5:
                    self.xVelocity = self.xVelocity + 0.5
            if k[K_a]:
                if self.xVelocity > -5:
                    self.xVelocity = self.xVelocity - 0.5
            if k[K_w]:
                if self.yVelocity > -5:
                    self.yVelocity = self.yVelocity - 0.5
            if k[K_s]:
                if self.yVelocity < 5:
                    self.yVelocity = self.yVelocity + 0.5
            if k[K_SPACE]:
                self.shoot = True

# ---------------------------------------------------------------


class SoccerBall:
    def __init__(self, x, y):
        self.image = os.getcwd() + r'\skins\myball.png'
        self.skin = pygame.image.load(self.image).convert_alpha()
        self.radius = 19  # its the radius
        self.rect = self.skin.get_rect()
        #pygame.draw.circle(self.skin, YELLOW, self.rect.center, self.radius)
        self.x = x #+ self.radius
        self.y = y #+ self.radius
        self.xVelocity = 0
        self.yVelocity = 0
        self.angle = 0
        self.inGoalLeft = False
        self.inGoalRight = False

    def move(self):

        self.inGoalLeft = False
        self.inGoalRight = False

        if self.xVelocity > 0:
            self.xVelocity -= friction
        if self.xVelocity < 0:
            self.xVelocity += friction
        if self.yVelocity > 0:
            self.yVelocity -= friction
        if self.yVelocity < 0:
            self.yVelocity += friction
        if self.xVelocity != 0:
            self.angle = math.degrees(math.atan(self.yVelocity/self.xVelocity))
        elif self.xVelocity == 0:
            self.angle = "/"
        if self.yVelocity > -0.01 and self.yVelocity < 0.01:
            self.yVelocity = 0
        if self.xVelocity > -0.01 and self.xVelocity < 0.01:
            self.xVelocity = 0

        if right_border_for_ball - int(self.x) <= 2 * self.radius:
            if int(self.y) in range(gate_top_corner_y, gate_bottom_corner_y):
                self.inGoalRight = True
            else:
                self.xVelocity = -self.xVelocity

        if abs(left_border_for_ball - int(self.x)) <= 5:
            if int(self.y) in range(gate_top_corner_y, gate_bottom_corner_y):
                self.inGoalLeft = True
            else:
                self.xVelocity = -self.xVelocity

        if bottom_border_for_ball - int(self.y) <= 2*self.radius:
            self.yVelocity = -self.yVelocity

        if abs(int(self.y) - top_border_for_players) <= 5:
            self.yVelocity = -self.yVelocity

        self.x += self.xVelocity
        self.y += self.yVelocity

    def draw(self):
        DS.blit(self.skin, (self.x, self.y))
        if sys.argv[1] == 'Admin':
            myfont = pygame.font.SysFont("Trebuchet MS", 12)
            angleToPrint = myfont.render(str(self.angle)[0:5] + " degrees", 1, GameVariables.YELLOW)
            velocityToPrint = myfont.render(str(math.sqrt(pow((self.xVelocity), 2) + pow((self.yVelocity),2)))[0:5], 1, GameVariables.YELLOW)
            DS.blit(angleToPrint,(self.x, self.y + 80))
            DS.blit(velocityToPrint, (self.x, self.y + 90))

    def do(self):
        self.move()
        self.draw()
