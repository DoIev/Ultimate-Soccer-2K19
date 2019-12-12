import os
import sys
import datetime  # evening, morning, etc
import sqlite3
import subprocess
import pygame
import pymsgbox
import re  # x and y coordinates for mouse
import math
import hashlib
import binascii
import GameVariables


# ---------------- SQL VARS
connection = None
sql_cursor = None
# ----------------

# ---------------- HOME VARS
circle_radius = 35.3
exit_m_x_coordinate = 519  # px
info_m_x_coordinate = 633  # px
play_m_x_coordinate = 750  # px
m_y_coordinate = 449  # px
# ---------------

# --------------- LOGIN PAGE VARS
user = ''
username = '- USERNAME -'
password = '- PASSWORD -'
username_first_time = True
password_first_time = True
username_input_box_active = False
password_input_box_active = False
clock = pygame.time.Clock()
# --------------

def send_data_to_database(x):
    """ the function receives a username and password and checks
    if the given details are same to the stored data in the game database
    if so, it will launch the menu, otherwise it will return an error """

    global connection
    global sql_cursor
    global user
    username, password = x.split(";")
    connection = sqlite3.connect(GameVariables.database)
    sql_cursor = connection.cursor()
    sql_cursor.execute(f"""SELECT password FROM users WHERE username = '{username}';""")
    result = sql_cursor.fetchone()
    if result is not None:
        if username == "Admin" and password == "Admin":
            answer = pymsgbox.confirm(text='Would you like to create a new user?', title='Admin permissions', buttons=['OK', 'Cancel'])

            if answer == 'OK':
                create_user()
            login = True
        else:  # if the user is not the Admin
            stored_password = result[0]
            if verify_password(stored_password, password):
                login = True
            else:
                login = False
        # ------------ send report to database
        if login is not False:
            try:
                connection = sqlite3.connect(GameVariables.database)
                sql_cursor = connection.cursor()
                sql_cursor.execute("""CREATE TABLE IF NOT EXISTS log(
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        connTime DATETIME,
                                        action STRING
                                        );""")
                connection.commit()
                sql_cursor.execute(f"""INSERT INTO log(connTime,action) VALUES(CURRENT_TIMESTAMP, '{username} logged in');""")
                connection.commit()
                connection.close()
            except:
                print("error: could not send this report to the database")
        # -------------------------------------

            user = username
            menu.currently_viewing = 0
            return
    pymsgbox.alert(text='Wrong username and/or password.', title='Error', button='OK')
    return


def connect_to_sql_database():
    """the function connects to the game database and makes sure that all the necessary tables
    in the database are exist, otherwise it creates them in order to allow the game to run
    on every computer, even its the first time running on a new computer"""
    global sql_cursor
    global connection
    try:
        connection = sqlite3.connect(GameVariables.database)
        sql_cursor = connection.cursor()
        sql_cursor.execute("""CREATE TABLE IF NOT EXISTS log(
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          connTime DATETIME,
                          action STRING
                          );""")
        connection.commit()
        sql_cursor.execute("""INSERT INTO log(connTime,action) VALUES(CURRENT_TIMESTAMP, 'login page opened');""")
        connection.commit()

        sql_cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            username TEXT,
                                            password TEXT,
                                            created DATETIME,
                                            played INTEGER,
                                            wins INTEGER,
                                            losses INTEGER,
                                            goals INTEGER,
                                            conceded INTEGER,
                                            clean_sheets INTEGER
                                            );""")
        connection.commit()
        sql_cursor.execute("""SELECT * FROM users WHERE username='Admin' AND password='Admin';""")
        if sql_cursor.fetchone() is None:
            sql_cursor.execute("""INSERT INTO users(username,password,created,played,wins,losses,goals,conceded,clean_sheets) 
                                  VALUES(?, ?, CURRENT_TIMESTAMP, 0,0,0,0,0,0);""", ('Admin', 'Admin'))
            connection.commit()
        connection.close()
        return True  # true (connected successfully)
    except:
        return False  # false (not connected)


def create_user():
    """the function allows the admin user to create a new user and insert his
    details to the game database. this function will only be used if the admin
    decides to create a new user. after the process, the function will raise a
    message box with the results of the process"""
    global connection
    global sql_cursor

    try:
        username_to_create = pymsgbox.prompt('Enter a username to create')

        while not check_username(username_to_create):
            username_to_create = pymsgbox.prompt('The requested username does not meet the requirements, or already taken.')

        password_to_create = pymsgbox.prompt('Enter a password. NOTICE: your password will remain encrypted on this computer.')
        while not check_password(password_to_create):
            password_to_create = pymsgbox.prompt('The requested password does not meet the requirements.')

        encrypted_password_to_create = hash_password(password_to_create)
        connection = sqlite3.connect(GameVariables.database)
        sql_cursor = connection.cursor()
        sql_cursor.execute("""INSERT INTO users(username,password,created,played,wins,losses,goals,conceded,clean_sheets) VALUES(?, ?, CURRENT_TIMESTAMP, 0,0,0,0,0,0);""",(username_to_create,encrypted_password_to_create))
        connection.commit()
        pymsgbox.alert(text='The user was created successfully', title='Admin Permissions', button='OK')

        # --------------- send report to database
        sql_cursor.execute("""CREATE TABLE IF NOT EXISTS log(
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    connTime DATETIME,
                                    action STRING
                                    );""")
        connection.commit()
        sql_cursor.execute(f"""INSERT INTO log(connTime,action) VALUES(CURRENT_TIMESTAMP, 'new user created - {username_to_create}');""")
        connection.commit()
        connection.close()
        # --------------------------------------
    except:
        pymsgbox.alert(text='Could not create the user.', title='Error', button='OK')


def check_username(usr):
    """the function receives a username and returns true if the username
    is fine and it is meeting with the requirements or false or not
    the length of the string must be between 4 to 8 chars, and
    the username must be available"""
    global connection
    global sql_cursor
    if usr is None:
        return False
    if len(usr) < 4 or len(usr) > 9:
        return False
    if " " in usr:
        return False
    connection = sqlite3.connect(GameVariables.database)
    sql_cursor = connection.cursor()
    search_for_existing_username = sql_cursor.execute(f"""SELECT * FROM users WHERE username = '{usr}';""")
    if len(search_for_existing_username.fetchall()) > 0:
        connection.close()
        return False
    connection.close()
    return True


def check_password(pwd):
    """the function receives a password and returns true of the password
    is longer than 4 characters and shorter than 9 chars. otherwise it
    will return false"""
    if pwd is None:
        return False
    if len(pwd) in range(3, 9):
        return True
    else:
        return False


def hash_password(password):  # special thanks to https://www.vitoshacademy.com/hashing-passwords-in-python/
    """Hash a password for storing it in our database safely."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')


def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password


class Menu:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.background_music_player = subprocess.Popen("python BackgroundMusicPlayer.py")  # play the music
        self.gameDisplay = pygame.display.set_mode((GameVariables.window_width, GameVariables.window_height))
        pygame.display.set_caption(f'{GameVariables.__game_name__} ~ by {GameVariables.__author__}')  # game title
        # --------------------------------------------------- ADDING ICON TO MENU
        icon = pygame.image.load(os.getcwd() + r'\new_menu\icon.png')
        icon = pygame.transform.scale(icon, (32, 32))
        surface = pygame.Surface(icon.get_size())
        key = (0, 0, 0)
        surface.set_colorkey(key)
        pygame.display.set_icon(icon)
        # -------------------------------------------------- CREATING THE BACKGROUND
        self.currently_viewing = -6
        self.clicking_sound = os.path.join(os.getcwd(), 'new_menu', "button_click.wav")
        self.menu_options_dictionary = {-6: os.getcwd() + r'\new_menu\firstpage_nothing.jpg',
                                        -5: os.getcwd() + r'\new_menu\firstpage_exit.jpg',
                                        -4: os.getcwd() + r'\new_menu\firstpage_info.jpg',
                                        -3: os.getcwd() + r'\new_menu\firstpage_play.jpg',
                                        -2: os.getcwd() + r'\new_menu\login\login.jpg',
                                        -1: os.getcwd() + r'\new_menu\login\login_hover_button.jpg',
                                        0: os.getcwd() + r'\new_menu\game_menu_selected_noting.png',
                                        1: os.getcwd() + r'\new_menu\game_menu_selected_game.png',
                                        2: os.getcwd() + r'\new_menu\game_menu_selected_watch.png',
                                        3: os.getcwd() + r'\new_menu\game_menu_selected_stat.png',
                                        4: os.getcwd() + r'\new_menu\game_menu_selected_info.png',
                                        5: os.getcwd() + r'\new_menu\info\info.jpg',
                                        6: os.getcwd() + r'\new_menu\info\info_hold_return.jpg',
                                        7: os.getcwd() + r'\new_menu\STATISTICS\stat.jpg',
                                        8: os.getcwd() + r'\new_menu\STATISTICS\stat_hold_return.jpg'}
        self.return_from_info_page_to = None
        self.sound = pygame.mixer.Sound(self.clicking_sound)  # defines the sound when choosing between options

        self.stat_games = None
        self.stat_wins = None
        self.stat_losses = None
        self.stat_wl_ratio = None
        self.stat_goals = None
        self.stat_goals_conceded = None
        self.stat_gc_ratio = None
        self.stat_clean_sheets = None
        self.stat_pc_games = None
        self.stat_pc_users = None

    def print_menu(self):
        background = pygame.image.load(self.menu_options_dictionary.get(self.currently_viewing))
        self.gameDisplay.blit(background, (0, 0))  # drawing the background
        # -------------- IF THE SCREEN IS THE LOGIN PAGE
        if self.currently_viewing in range(-2, 0):
            global username, password
            global username_input_box_active
            global password_input_box_active
            font = pygame.font.Font(None, 32)
            username_input_box = pygame.Rect(894.5 - 70, 190, 140, 32)
            password_input_box = pygame.Rect(894.5 - 70, 260, 140, 32)
            entry_color = (232, 232, 232)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.background_music_player.kill()
                    pygame.quit()  # Quit pygame if window in closed
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # If the user clicked on the username_input_box rect.
                    if username_input_box.collidepoint(event.pos):
                        # Toggle the username_input_box_active variable.
                        global username_first_time
                        if username_first_time is True:
                            username = ''
                            username_first_time = False
                        username_input_box_active = not username_input_box_active
                    else:
                        username_input_box_active = False
                    if password_input_box.collidepoint(event.pos):
                        global password_first_time
                        if password_first_time is True:
                            password = ''
                            password_first_time = False
                        password_input_box_active = not password_input_box_active
                    else:
                        password_input_box_active = False
                    # Change the current color of the input box.
                if event.type == pygame.KEYDOWN:
                    if username_input_box_active:
                        if event.key == pygame.K_BACKSPACE:
                            username = username[:-1]
                        elif len(username) <= 8:
                            username += event.unicode
                    if password_input_box_active:
                        if event.key == pygame.K_BACKSPACE:
                            password = password[:-1]
                        elif len(password) <= 8:
                            password += event.unicode

            # Render the current text.
            username_txt_surface = font.render(username, True, (222, 17, 102))
            if password_first_time:
                password_txt_surface = font.render(password, True, (222, 17, 102))
            else:
                password_txt_surface = font.render(len(password) * '*', True, (222, 17, 102))
            # Blit the text.
            username_text_rect = username_txt_surface.get_rect(center=(
                username_input_box.x + username_input_box.width / 2,
                username_input_box.y + username_input_box.height / 2))
            password_text_rect = password_txt_surface.get_rect(center=(
                password_input_box.x + password_input_box.width / 2,
                password_input_box.y + password_input_box.height / 2))

            menu.gameDisplay.blit(username_txt_surface, (username_text_rect))
            menu.gameDisplay.blit(password_txt_surface, (password_text_rect))
            # Blit the username_input_box rect.
            pygame.draw.rect(menu.gameDisplay, entry_color, username_input_box, 2)
            pygame.draw.rect(menu.gameDisplay, entry_color, password_input_box, 2)
        # -------------- END OF IF TERM (LOGIN PAGE)
        # -------------- IF THE SCREEN IS THE MENU ITSELF
        elif self.currently_viewing in range(0, 5):
            font = pygame.font.SysFont("SecularOne-Regular", 42)

            if datetime.datetime.now().hour in range(6, 11):  # boker
                welcome_message = u"בוקר טוב, "
            elif datetime.datetime.now().hour in range(11, 18):  # noon
                welcome_message = u"צוהריים טובים, "
            elif datetime.datetime.now().hour in range(18, 21):  # evening
                welcome_message = u"ערב טוב, "
            else:  # night
                welcome_message = u"לילה טוב, "

            reversed_text = welcome_message[::-1]  # because the hebrew, we need to reverse the text
            welcome_message = font.render(user + reversed_text, 1, GameVariables.WHITE)
            self.gameDisplay.blit(welcome_message, (800, 80))
        # -------------- END OF TERM (MENU)
        pygame.display.update()
        return

    def get_user_statistics(self):
        connection = sqlite3.connect(GameVariables.database)
        sql_cursor = connection.cursor()
        # sql_cursor.execute(f"""SELECT created FROM users WHERE username = '{user}';""")
        # joined = sql_cursor.fetchone()[0]  # its a tuple.
        sql_cursor.execute(f"""SELECT wins FROM users WHERE username = '{user}';""")
        self.stat_wins = int(sql_cursor.fetchone()[0])
        sql_cursor.execute(f"""SELECT losses FROM users WHERE username = '{user}';""")
        self.stat_losses = int(sql_cursor.fetchone()[0])
        if self.stat_losses == 0:
            self.stat_wl_ratio = '-'
        else:
            self.stat_wl_ratio = str(self.stat_wins / self.stat_losses)[0:3]
        sql_cursor.execute(f"""SELECT played FROM users WHERE username = '{user}';""")
        self.stat_games = int(sql_cursor.fetchone()[0])
        sql_cursor.execute(f"""SELECT goals FROM users WHERE username = '{user}';""")
        self.stat_goals = int(sql_cursor.fetchone()[0])
        sql_cursor.execute(f"""SELECT conceded FROM users WHERE username = '{user}';""")
        self.stat_goals_conceded = int(sql_cursor.fetchone()[0])
        if self.stat_goals_conceded == 0:
            self.stat_gc_ratio = '-'
        else:
            self.stat_gc_ratio = str(self.stat_goals / self.stat_goals_conceded)[0:3]
        sql_cursor.execute(f"""SELECT clean_sheets FROM users WHERE username = '{user}';""")
        self.stat_clean_sheets = int(sql_cursor.fetchone()[0])
        sql_cursor.execute("""SELECT SUM(played) FROM users;""")
        self.stat_pc_games = int(sql_cursor.fetchone()[0])
        sql_cursor.execute("""SELECT COUNT(id) FROM users;""")
        self.stat_pc_users = int(sql_cursor.fetchone()[0])

    def print_statistics(self):
        font = pygame.font.SysFont("SecularOne-Regular", 42)

        self.gameDisplay.blit(font.render(str(self.stat_games), 1, GameVariables.WHITE), (710, 165))  # games
        self.gameDisplay.blit(font.render(str(self.stat_wins), 1, GameVariables.WHITE), (585, 165))  # wins
        self.gameDisplay.blit(font.render(str(self.stat_losses), 1, GameVariables.WHITE), (460, 165))  # losses
        self.gameDisplay.blit(font.render(str(self.stat_wl_ratio), 1, GameVariables.WHITE), (330, 165))  # wl ratio
        self.gameDisplay.blit(font.render(str(self.stat_goals), 1, GameVariables.WHITE), (710, 312))  # goals
        self.gameDisplay.blit(font.render(str(self.stat_goals_conceded), 1, GameVariables.WHITE), (585, 312))  # conceded
        self.gameDisplay.blit(font.render(str(self.stat_gc_ratio), 1, GameVariables.WHITE), (460, 312))  # gc ratio
        self.gameDisplay.blit(font.render(str(self.stat_clean_sheets), 1, GameVariables.WHITE), (330, 312))  # clean sheets
        self.gameDisplay.blit(font.render(str(self.stat_pc_games), 1, GameVariables.WHITE), (140, 312))  # total games on pc
        self.gameDisplay.blit(font.render(str(self.stat_pc_users), 1, GameVariables.WHITE), (140, 165))  # total users on pc
        pygame.display.update()


menu = Menu()


def main():
    while True:
        events()
        draw_menu_by_cursor()


def events():  # check quit - important!!
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            menu.background_music_player.kill()
            pygame.quit()  # Quit pygame if window in closed
            sys.exit()


def draw_menu_by_cursor():

    cursor_x_pos = int(re.findall('\d+', str(pygame.mouse.get_pos()))[0])
    cursor_y_pos = int(re.findall('\d+', str(pygame.mouse.get_pos()))[1])

    if menu.currently_viewing in range(-6, -2):  # HOME
        if math.hypot(exit_m_x_coordinate - cursor_x_pos, m_y_coordinate - cursor_y_pos) <= circle_radius:  # exit
            setattr(menu, 'currently_viewing', -5)
            if pygame.mouse.get_pressed()[0]:
                menu.sound.play()
                pygame.display.quit()  # Quit pygame if window in closed
                sys.exit()

        elif math.hypot(info_m_x_coordinate - cursor_x_pos, m_y_coordinate - cursor_y_pos) <= circle_radius:  # info
            setattr(menu, 'currently_viewing', -4)
            if pygame.mouse.get_pressed()[0]:
                menu.sound.play()
                menu.return_from_info_page_to = menu.currently_viewing
                setattr(menu, 'currently_viewing', 5)

        elif math.hypot(play_m_x_coordinate - cursor_x_pos, m_y_coordinate - cursor_y_pos) <= circle_radius:  # play
            setattr(menu, 'currently_viewing', -3)
            if pygame.mouse.get_pressed()[0]:
                menu.sound.play()
                menu.currently_viewing = -2

    elif menu.currently_viewing in range(-2, 0):  # LOGIN
        if cursor_x_pos in range(835, 940) and cursor_y_pos in range(374, 411):
            menu.currently_viewing = -1
            if pygame.mouse.get_pressed()[0]:
                connected = connect_to_sql_database()  # its a boolean variable.
                if not connected:
                    pymsgbox.alert(text='Could not connect to the Game Database.', title='Error', button='OK')
                else:
                    send_data_to_database(username + ";" + password)
        else:
            menu.currently_viewing = -2

    elif menu.currently_viewing in range(5, 7):  # INFO
        if cursor_x_pos in range(1098, 1256) and cursor_y_pos in range(485, 511):
            menu.currently_viewing = 6
            if pygame.mouse.get_pressed()[0]:
                menu.sound.play()
                menu.currently_viewing = menu.return_from_info_page_to
                menu.return_from_info_page_to = None
        else:
            menu.currently_viewing = 5

    elif menu.currently_viewing in range(7, 9):  # STAT
        menu.get_user_statistics()
        menu.print_statistics()
        if cursor_x_pos in range(1098, 1256) and cursor_y_pos in range(485, 511):
            menu.currently_viewing = 8
            if pygame.mouse.get_pressed()[0]:
                menu.sound.play()
                menu.currently_viewing = 0
        else:
            menu.currently_viewing = 7

    else:  # if the screen is the main menu
        if cursor_x_pos in range(513, 643) and cursor_y_pos in range(215, 345):  # info
            menu.currently_viewing = 4
            if pygame.mouse.get_pressed()[0]:
                menu.sound.play()
                menu.return_from_info_page_to = menu.currently_viewing
                setattr(menu, 'currently_viewing', 5)

        elif cursor_x_pos in range(694, 824) and cursor_y_pos in range(215, 345):  # stat
            menu.currently_viewing = 3
            if pygame.mouse.get_pressed()[0]:
                menu.sound.play()
                menu.currently_viewing = 7
        elif cursor_x_pos in range(875, 1005) and cursor_y_pos in range(215, 345):  # watch
            menu.currently_viewing = 2
            if pygame.mouse.get_pressed()[0]:
                menu.sound.play()
        elif cursor_x_pos in range(1056, 1186) and cursor_y_pos in range(215, 345):  # single player
            menu.currently_viewing = 1
            if pygame.mouse.get_pressed()[0]:
                menu.sound.play()
                menu.background_music_player.kill()
                pygame.display.quit()
                os.system(f"python SinglePlayer.py {user}")
                sys.exit()

        else:
            if cursor_y_pos not in range(215, 345):
                menu.currently_viewing = 0

    menu.print_menu()


if __name__ == "__main__":
    pygame.init()
    main()


