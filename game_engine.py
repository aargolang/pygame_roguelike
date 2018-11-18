import os
import csv
import random

import roguelike


import pygame
from pygame.locals import *
from pygame.compat import geterror

# my libraries
import game_NPCs
import game_entities

# asset directories
main_dir = os.path.split(os.path.abspath(__file__))[0]
graphics_dir = os.path.join(main_dir, 'graphics')
sound_dir = os.path.join(main_dir, 'sound')
level_dir = os.path.join(main_dir, 'levels')

# initialize game essentials
pygame.mixer.init(22050, -16, 8, 4096)      # not currently used
pygame.font.init()
pygame.joystick.init()
joystick_count = pygame.joystick.get_count()


# load_image
# concatenates the name to the graphics directory
# and checks to see if that file path works,
# throws an error if unsuccessful
# scales up graphics by 2
# returns: image
def load_image(name):
    fullpath = os.path.join(graphics_dir, name)
    try:
        image = pygame.image.load(fullpath)
    except pygame.error:
        print('cannot load image', fullpath)
        raise SystemExit(str(geterror()))

    # upscale loaded images by 2x and 2y
    dimensions = (2 * image.get_width(), 2 * image.get_height())
    image = pygame.transform.scale(image, dimensions)

    return image

# load_image_rect
# concatinates the name to the graphics directory
# and checks to see if that file path works, throws an error
# if unsuccessful
# returns: image, rect
def load_image_rect(name, colorkey=None):
    """loads image and rect for sprites usually"""
    fullpath = os.path.join(graphics_dir, name)
    try:
        image = pygame.image.load(fullpath)
    except pygame.error:
        print('cannot load image', fullpath)
        raise SystemExit(str(geterror()))
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)

    # upscale loaded images by 2x and 2y
    dimensions = (2 * image.get_width(), 2 * image.get_height())
    image = pygame.transform.scale(image, dimensions)

    return image, image.get_rect()

# Class Level
# stores the level data in memory
# TODO: make it a singleton once the levels are jsonified
class Level:
    def __init__(self, level_p, tile_p=None):
        self.level_path = os.path.join(level_dir, level_p)
        self.warp_list = None
        self.npcs = []

        if tile_p is not None:
            self.tile_path = tile_p

    def set_warps(self, warps):
        self.warp_list = warps
        
    def add_npc(self, npc):
        self.npcs.append(npc)

# CLASS LevelWarp
# handles changing the level and moving player to correct location
class LevelWarp:
    def __init__(self, level, x, y):
        self.new_level = level
        self.new_x = x
        self.new_y = y

# CLASS Game
# stores screen resolution and background color
# initializes the players starting location
# define control and drawing methods
# TODO: add wall member as array of tiles
# TODO: add floor member as array of tiles
class Game:
    black = (20, 12, 28)
    white = (223, 239, 215)
    blue = (89, 125, 207)
    background_color = black
    # screen size (in 32*32 squares) needs to be odd numbers because of player in center
    screen_size = (45, 23)
    screen_resolution = (screen_size[0] * 32, screen_size[1] * 32)
    screen_x_buffer = int((screen_size[0]-1)/2)
    screen_y_buffer = int((screen_size[1]-1)/2)
    key_delay = 200
    key_repeat = 50
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 32)

    def __init__(self):
        pygame.init()
        self.font_1 = pygame.font.Font('fonts/victor-pixel.ttf', 32)

        pygame.key.set_repeat(self.key_delay, self.key_repeat)
        self.screen = pygame.display.set_mode(self.screen_resolution)

        # setup display and background color/size
        pygame.display.set_icon(pygame.image.load('graphics/icon.png'))
        pygame.display.set_caption('u can sav the world!')
        self.background = pygame.Surface(self.screen_resolution)
        self.background.fill(self.background_color)

        # TODO: this wont work. need to only have current level in memory
        # declare levels
        self.test = Level('test.csv')
        self.town_level = Level('town.csv')
        self.dungeon_1_level = Level('dungeon_1.csv')
        self.dungeon_2_level = Level('dungeon_2.csv')
        self.forest_1_level = Level('forest_1.csv')

        # set warps
        self.town_level.set_warps({
            '25,19': LevelWarp(self.dungeon_1_level, 17, 18),
            '14,4': LevelWarp(self.dungeon_1_level, 8, 2),
            '46,17': LevelWarp(self.forest_1_level, 2, 30)
        })
        self.dungeon_1_level.set_warps({
            '17,19': LevelWarp(self.town_level, 24, 19),
            '8,1': LevelWarp(self.town_level, 13, 4),
            '36,18': LevelWarp(self.dungeon_2_level, 5, 2)
        })
        self.dungeon_2_level.set_warps({
            '5,1': LevelWarp(self.dungeon_1_level, 35, 18)
        })
        self.forest_1_level.set_warps({
            '1,30': LevelWarp(self.town_level, 45, 17)
        })

        # set friendlies
        self.town_level.add_npc(game_NPCs.Friendly(10, 7))
        self.town_level.add_npc(game_NPCs.Friendly(25, 5))
        self.town_level.add_npc(game_NPCs.Friendly(43, 7))
        self.town_level.add_npc(game_NPCs.Friendly(13, 32))
        self.town_level.add_npc(game_NPCs.Friendly(23, 27))
        self.town_level.add_npc(game_NPCs.Friendly(36, 29))

        # set objects
        self.town_level.add_npc(game_entities.Chest(7, 4))

        # initialize game to first level
        self.current_map = None
        self.current_level = None
        self.player = None

        # make the wall and floor class
        self.floor_1 = []

        self.floor_1.append(load_image(os.path.join(graphics_dir, "floor_1_1.png")))
        self.floor_1.append(load_image(os.path.join(graphics_dir, "floor_1_2.png")))
        self.floor_1.append(load_image(os.path.join(graphics_dir, "floor_1_3.png")))
        self.floor_1.append(load_image(os.path.join(graphics_dir, "floor_1_4.png")))
        self.floor_1.append(load_image(os.path.join(graphics_dir, "floor_1_5.png")))
        self.floor_1.append(load_image(os.path.join(graphics_dir, "floor_1_6.png")))
        self.floor_1.append(load_image(os.path.join(graphics_dir, "floor_1_7.png")))
        self.floor_1.append(load_image(os.path.join(graphics_dir, "floor_1_8.png")))
        self.floor_1.append(load_image(os.path.join(graphics_dir, "floor_1_9.png")))
        self.floor_2 = []
        self.floor_2.append(load_image(os.path.join(graphics_dir, "floor_2.png")))
        self.wall = []
        self.wall.append(load_image(os.path.join(graphics_dir, "wall_1.png")))
        self.wall.append(load_image(os.path.join(graphics_dir, "wall_2.png")))
        self.warp = load_image(os.path.join(graphics_dir, "warp.png"))

    # LOAD LEVEL
    # load the level passed in into memory
    # levels character values by convention
    # corresponding wall floor class is +/- 60
    # floors 1('.'):        1 - 20
    # floors 2(','):        21 - 40
    # floors 3('`'):        41 - 60
    # walls 1('1'):         61 - 80
    # walls 2('2'):         81 - 100
    # walls 3('3'):         101 - 120
    # warp:                 0
    # nullspace('_'):       -1
    def load_level(self, lev):
        if self.current_map is not None:
            self.current_map.clear()
        self.current_map = list(csv.reader(open(lev.level_path)))
        for i in range(len(self.current_map)):
            for j in range(len(self.current_map[0])):
                if self.current_map[i][j] == '_':  # set null
                    self.current_map[i][j] = -1
                elif self.current_map[i][j] == '.':  # set floors
                    rand = random.randint(1, 400)
                    if rand > 50:
                        self.current_map[i][j] = 1
                    elif rand > 45:
                        self.current_map[i][j] = 2
                    elif rand > 40:
                        self.current_map[i][j] = 3
                    elif rand > 35:
                        self.current_map[i][j] = 4
                    elif rand > 30:
                        self.current_map[i][j] = 5
                    elif rand > 25:
                        self.current_map[i][j] = 6
                    elif rand > 20:
                        self.current_map[i][j] = 7
                    elif rand > 15:
                        self.current_map[i][j] = 8
                    else:
                        self.current_map[i][j] = 9

                elif self.current_map[i][j] == ',':
                    self.current_map[i][j] = 21
                elif self.current_map[i][j] == '`':
                    self.current_map[i][j] = 41
                elif self.current_map[i][j] == '1':  # set walls
                    self.current_map[i][j] = 61
                elif self.current_map[i][j] == '2':
                    self.current_map[i][j] = 81
                elif self.current_map[i][j] == '3':
                    self.current_map[i][j] = 101

        # set the level warps in the current_map
        if lev.warp_list is not None:
            for a, b in lev.warp_list.items():
                warp_point = a.split(',')
                self.current_map[int(warp_point[1])][int(warp_point[0])] = 0

        # set current_level
        self.current_level = lev

    # CONTROL TICK
    # this function will handle all input functions
    # returns false when game is ready to quit
    def control_tick(self):

        if joystick_count > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()

        pos_east = self.current_map[self.player.y][self.player.x + 1]
        pos_west = self.current_map[self.player.y][self.player.x - 1]
        pos_north = self.current_map[self.player.y - 1][self.player.x]
        pos_south = self.current_map[self.player.y + 1][self.player.x]

        # get enemies in close proximity and forbid moving in those directions
        # need to detect enemies that are adjacent to player
        # TODO: this is linear time and need to be improved
        for npc in self.current_level.npcs:
            if npc.x == self.player.x:
                if npc.y == (self.player.y + 1):
                    print("south")
                    pos_south = 61
                    # collide with npc to the south
                elif npc.y == (self.player.y - 1):
                    print("north")
                    pos_north = 61
                    # collide with npc to the north
            elif npc.y == self.player.y:
                if npc.x == (self.player.x + 1):
                    print("east")
                    pos_east = 61
                    # collide with npc to the east
                elif npc.x == (self.player.x - 1):
                    print("west")
                    pos_west = 61
                    # collide with npc to the west

        while True:
            # improve performance by waiting to draw until new event is on event queue
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                return False

            if event.type == KEYDOWN:
                if event.key == K_RIGHT and (pos_east < 61):
                    self.player.x += 1
                    return True
                elif event.key == K_LEFT and (pos_west < 61):
                    self.player.x -= 1
                    return True
                elif event.key == K_UP and (pos_north < 61):
                    self.player.y -= 1
                    return True
                elif event.key == K_DOWN and (pos_south < 61):
                    self.player.y += 1
                    return True
                elif event.key == K_ESCAPE:
                    return False

            # xinput controls
            # need to implement repeat on hold down. no pygame methods available for this
            if event.type == JOYHATMOTION:
                hat = joystick.get_hat(0)
                if hat == (1, 0) and (pos_east < 61):
                    self.player.x += 1
                    return True
                if hat == (-1, 0) and (pos_west < 61):
                    self.player.x -= 1
                    return True
                if hat == (0, 1) and (pos_north < 61):
                    self.player.y -= 1
                    return True
                if hat == (0, -1) and (pos_south < 61):
                    self.player.y += 1
                    return True

    # DRAW TICK
    # this function handles all of the rendering functionality
    # has no return value
    def draw_tick(self):
        # check for warp
        pos = self.current_map[self.player.y][self.player.x]
        if pos == 0:
            position_key = str(self.player.x) + ',' + str(self.player.y)
            if self.current_level.warp_list[position_key]:
                warp = self.current_level.warp_list[position_key]
                self.load_level(warp.new_level)
                self.player.x = warp.new_x
                self.player.y = warp.new_y

        # draw the current_map matrix
        # scroll the map based on the player
        # TODO: fix this to include variable resolution values
        self.screen.blit(self.background, (0, 0))
        for x in range(self.player.x - self.screen_x_buffer, self.player.x + self.screen_x_buffer + 1):
            for y in range(self.player.y - self.screen_y_buffer, self.player.y + self.screen_y_buffer + 1):
                if x in range(len(self.current_map[0])) and y in range(len(self.current_map)):
                    if self.current_map[y][x] > 80:
                        self.screen.blit(self.wall[1], ((x - self.player.x + self.screen_x_buffer) * 32,
                                                        (y - self.player.y + self.screen_y_buffer) * 32))
                    elif self.current_map[y][x] > 60:
                        self.screen.blit(self.wall[0], ((x - self.player.x + self.screen_x_buffer) * 32,
                                                        (y - self.player.y + self.screen_y_buffer) * 32))
                    elif self.current_map[y][x] > 20:
                        self.screen.blit(self.floor_2[0], ((x - self.player.x + self.screen_x_buffer) * 32,
                                                         (y - self.player.y + self.screen_y_buffer) * 32))
                    elif self.current_map[y][x] > 0:
                        self.screen.blit(self.floor_1[self.current_map[y][x]-1],
                                         ((x - self.player.x + self.screen_x_buffer) * 32,
                                          (y - self.player.y + self.screen_y_buffer) * 32))
                    elif self.current_map[y][x] == 0:
                        self.screen.blit(self.warp, ((x - self.player.x + self.screen_x_buffer) * 32,
                                                     (y - self.player.y + self.screen_y_buffer) * 32))

        # update and draw npcs on the screen
        if len(self.current_level.npcs) > 0:
            for npc in self.current_level.npcs:
                npc.update(self.player, self.current_map)

                if npc.x in range(len(self.current_map[0])) and npc.y in range(len(self.current_map)):
                    self.screen.blit(npc.image, ((npc.x - self.player.x + self.screen_x_buffer) * 32,
                                                 (npc.y - self.player.y + self.screen_y_buffer) * 32))

        # draw player in the center of the screen
        self.screen.blit(self.player.image, (self.screen_x_buffer * 32, self.screen_y_buffer * 32))
        pygame.display.flip()

    # main game loop
    def play(self):
        while True:
            self.draw_tick()
            # return if control returns false
            if not self.control_tick():
                return

    def new_game(self):
        # TODO: consolidate all npc spawn points
        self.load_level(self.town_level)                # starting level
        self.player = game_entities.Player(20,20)
        self.dungeon_1_level.add_npc(game_NPCs.Enemy(4, 18))      # new game
        self.dungeon_1_level.add_npc(game_NPCs.Enemy(4, 4))       # new game
        self.dungeon_1_level.add_npc(game_NPCs.Enemy(32, 2))      # new game
        # self.dungeon_1_level.add_npc(Enemy(32, 17))     # new game
        self.dungeon_1_level.add_npc(game_NPCs.Enemy(32, 21))     # new game
        self.test.add_npc(game_NPCs.Enemy(3, 3))
        self.test.add_npc(game_NPCs.Friendly(31, 20))
        self.play()

    def main_menu(self):
        resolution_672_480 = (21, 15)
        resolution_1056_608 = (33, 19)
        resolution_1440_736 = (45, 23)

        while True:
            # declare menues
            menu_main = [
                self.font_1.render('(n)ew game', False, self.white),
                self.font_1.render('change (r)esolution', False, self.white),
                self.font_1.render('(q)uit', False, self.white)
            ]
            menu_resolution = [
                self.font_1.render('(1) 672x480', False, self.white),
                self.font_1.render('(2) 1056x608', False, self.white),
                self.font_1.render('(3) 1440x736', False, self.white)

            ]

            # draw main menu to screen
            self.screen.blit(self.background, (0, 0))
            for i in range(len(menu_main)):
                self.screen.blit(menu_main[i],
                                 (32 * int(self.screen_x_buffer / 2),
                                 (32 * int(self.screen_y_buffer / 2)) + (32 * i)))

            pygame.display.flip()
            event = pygame.event.wait()

            # get user input
            if event.type == KEYDOWN:
                if event.key == K_n:
                    return 'new'
                elif event.key == K_r:
                    res_menu = True
                    while res_menu is True:
                        # display resolution menu
                        self.screen.blit(self.background, (0, 0))
                        for i in range(len(menu_resolution)):
                            self.screen.blit(menu_resolution[i],
                                             (32 * int(self.screen_x_buffer / 2),
                                              (32 * int(self.screen_y_buffer / 2)) + (32 * i)))

                        pygame.display.flip()
                        event = pygame.event.wait()

                        # get user input
                        if event.type == KEYDOWN:
                            if event.key == K_1:
                                self.screen_size = resolution_672_480
                                res_menu = False
                            elif event.key == K_2:
                                self.screen_size = resolution_1056_608
                                res_menu = False
                            elif event.key == K_3:
                                self.screen_size = resolution_1440_736
                                res_menu = False

                        # adjust game to new resolution
                        self.screen_resolution = (self.screen_size[0] * 32, self.screen_size[1] * 32)
                        self.screen_x_buffer = int((self.screen_size[0]-1)/2)
                        self.screen_y_buffer = int((self.screen_size[1]-1)/2)
                        self.screen = pygame.display.set_mode(self.screen_resolution)
                        self.background = pygame.Surface(self.screen_resolution)
                        self.background.fill(self.background_color)

                elif event.key == K_q:
                    return 'quit'
                elif event.key == K_ESCAPE:
                    return 'quit'
            elif event.type == pygame.QUIT:
                return 'quit'

    def run(self):
        selection = self.main_menu()
        if selection == 'new':
            # TODO music needs to change based on level
            # pygame.mixer.music.load('music/level_1.ogg')
            # pygame.mixer.music.play(-1)
            self.new_game()

        elif selection == 'quit':
            return