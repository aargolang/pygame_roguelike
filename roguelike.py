import os
import pygame
import csv
from pygame.locals import *
from pygame.compat import geterror

pygame.mixer.init(22050, -16, 8, 4096)

# TODO
# - possibly reduce memory usage for large maps by only storing the walls
# - figure out how to load enemies into the levels
# - only render a new frame after user input to save processing time
# - clean up floor and wall graphics implementation

# set global varbarians to the source folder
# and subfolders
main_dir = os.path.split(os.path.abspath(__file__))[0]
graphics_dir = os.path.join(main_dir, 'graphics')
sound_dir = os.path.join(main_dir, 'sound')
level_dir = os.path.join(main_dir, 'levels')

# xinput settings
pygame.joystick.init()
joystick_count = pygame.joystick.get_count()


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


# load_image
# concatinates the name to the graphics directory
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
    image = image.convert()

    # upscale loaded images by 2x and 2y
    dimensions = (2 * image.get_width(), 2 * image.get_height())
    image = pygame.transform.scale(image, dimensions)

    return image


# CLASS Player
# stores player location
# stores player image and rect
# TODO: add player stats when battle system is made
class Player(pygame.sprite.Sprite):                 # initialize
    start_x = 27                                    # global starting x pos                                     DEBUG
    start_y = 27                                    # global starting y pos                                     DEBUG

    def __init__(self):                             # player default constructor
        pygame.sprite.Sprite.__init__(self)         # initialize player as a default sprite
        self.image, self.rect = load_image_rect(    # load player.bmp
            "player.bmp"
        )

        self.x = self.start_x                       # set starting x position
        self.y = self.start_y                       # set starting y position


class LevelWarp:
    def __init__(self, level, x, y):
        self.new_level = level
        self.new_x = x
        self.new_y = y


# levels character values by convention
# floors:   0 - 20
# walls:    21 - 38
# warp:     -1
class Level:
    def __init__(self, level_p, tile_p=None):
        self.level_path = os.path.join(level_dir, level_p)
        self.warp_list = None
        if tile_p is not None:
            self.tile_path = tile_p

    def set_warps(self, warps):
        self.warp_list = warps


# CLASS Game
# stores screen resolution and background color
# initializes the players starting location
# define control and drawing methods
# TODO: store current level, and init player starting location and level
# TODO: add wall member as array of tiles
# TODO: add floor member as array of tiles
# TODO: add current_map as char array
# TODO: define load_level() function
class Game:
    bg_color = (0, 0, 0)                            # background filler color
    screen_resolution = (544, 544)                  # on screen window size

    def __init__(self):                             # def constructor for game
        self.screen = pygame.display.set_mode(      # set screen size to...
            self.screen_resolution                  # screen_resolution
        )
        self.background = pygame.Surface(           # set background to...
            self.screen_resolution                  # size of screen
        ).convert()                                 # convert background to a surface
        self.background.fill(                       # set background to...
            self.bg_color                           # bg_color
        )

        # declare levels
        self.town_level = Level('town.csv')
        self.dungeon_1_level = Level('dungeon_1.csv')

        # set warps
        self.town_level.set_warps({
            '33,27': LevelWarp(self.dungeon_1_level, 25, 24),
            '22,12': LevelWarp(self.dungeon_1_level, 16, 8)
        })
        self.dungeon_1_level.set_warps({
            '25,25': LevelWarp(self.town_level, 32, 27),
            '16,7': LevelWarp(self.town_level, 21, 12)
        })

        self.current_map = None
        self.current_level = self.town_level
        self.load_level(self.town_level)

        self.player = Player()                      # initialize a player

        # TODO fix this hacky loading of walls and floors
        # make the wall and floor class
        self.floor = load_image(os.path.join(graphics_dir, "floor.bmp"))
        # dimensions = (2 * self.floor.get_width(), 2 * self.floor.get_height())
        # self.floor = pygame.transform.scale(self.floor, dimensions)

        self.wall = load_image(os.path.join(graphics_dir, "wall.bmp"))
        # dimensions = (2 * self.wall.get_width(), 2 * self.wall.get_height())
        # self.wall = pygame.transform.scale(self.wall, dimensions)
        self.warp = load_image(os.path.join(graphics_dir, "warp.bmp"))

    # LOAD LEVEL
    # load the level passed in into memory
    def load_level(self, lev):
        self.current_map = list(csv.reader(open(lev.level_path)))
        for a, b in lev.warp_list.items():
            warp_point = a.split(',')
            self.current_map[int(warp_point[1])][int(warp_point[0])] = '-1'

    # CONTROL TICK
    # this function will handle all input functions
    # returns false when game is ready to quit
    def control_tick(self):
        pos_right = self.current_map[self.player.y][self.player.x + 1]
        pos_left = self.current_map[self.player.y][self.player.x - 1]
        pos_up = self.current_map[self.player.y - 1][self.player.x]
        pos_down = self.current_map[self.player.y + 1][self.player.x]
        pos = self.current_map[self.player.y][self.player.x]

        if pos == '-1':
            position_key = str(self.player.x) + ',' + str(self.player.y)
            if self.current_level.warp_list[position_key]:
                warp = self.current_level.warp_list[position_key]
                self.load_level(warp.new_level)
                self.current_level = warp.new_level
                self.player.x = warp.new_x
                self.player.y = warp.new_y

        for event in pygame.event.get():
            # key down controls
            if event.type == KEYDOWN:
                # making code less wordy

                if event.key == K_RIGHT:
                    if pos_right != '1':
                        self.player.x += 1
                elif event.key == K_LEFT and (pos_left != '1'):
                    self.player.x -= 1
                elif event.key == K_UP and (pos_up != '1'):
                    self.player.y -= 1
                elif event.key == K_DOWN and (pos_down != '1'):
                    self.player.y += 1
                elif event.key == K_ESCAPE:
                    return False

        # xinput controls
        # currently sends the player at lightspeed in whatever direction
        # needs delay or something
        if joystick_count > 0:
            # making code less wordy
            player = self.player
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            hat = joystick.get_hat(0)
            if hat == (1, 0):
                player.x += 1
            if hat == (-1, 0):
                player.x -= 1
            if hat == (0, 1):
                player.y -= 1
            if hat == (0, -1):
                player.y += 1

        return True

    # DRAW TICK
    # this function handles all of the rendering functionality
    # has no return value
    def draw_tick(self):
        self.screen.blit(self.background, (0, 0))

        # draw the test_map matrix
        # scroll the map based on the player
        # TODO: fix this to include variable resolution values
        for x in range(self.player.x - 8, self.player.x + 9):
            for y in range(self.player.y - 8, self.player.y + 9):
                if self.current_map[y][x] == '1':
                    self.screen.blit(self.wall, ((x - self.player.x + 8) * 32, (y - self.player.y + 8) * 32))
                elif self.current_map[y][x] == '0':
                    self.screen.blit(self.floor, ((x - self.player.x + 8) * 32, (y - self.player.y + 8) * 32))
                elif self.current_map[y][x] == '-1':
                    self.screen.blit(self.warp, ((x - self.player.x + 8) * 32, (y - self.player.y + 8) * 32))

        # draw player in the center of the screen
        self.screen.blit(self.player.image, (8 * 32, 8 * 32))
        pygame.display.flip()

    # main game loop
    def run(self):
        while 1:
            # return if control returns false
            if not self.control_tick():
                return

            self.draw_tick()


def main():
    pygame.init()
    pygame.key.set_repeat(200, 50)
    new_game = Game()
    new_game.run()

    return


main()