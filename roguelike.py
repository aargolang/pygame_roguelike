import os
import pygame
import csv
from pygame.locals import *
from pygame.compat import geterror

pygame.mixer.init(22050, -16, 8, 4096)

# TODO
# - possibly reduce memory usage for large maps by only storing the walls
# - figure out how to load enemies into the levels
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
    start_x = 22                                    # global starting x pos                                     DEBUG
    start_y = 20                                    # global starting y pos                                     DEBUG

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
# corresponding wall floor class is +/- 60
# floors 1('.'):        1 - 20
# floors 2(','):        21 - 40
# floors 3('`'):        41 - 60
# walls 1('1'):         61 - 80
# walls 2('2'):         81 - 100
# walls 3('3'):         101 - 120
# warp:                 0
# nullspace('_'):       -1
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


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image_rect('enemy.bmp')
        self.x_pos = x
        self.y_pos = y


class Friendly(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image_rect('friendly.bmp')
        self.x_pos = x
        self.y_pos = y


# CLASS Game
# stores screen resolution and background color
# initializes the players starting location
# define control and drawing methods
# TODO: add wall member as array of tiles
# TODO: add floor member as array of tiles
class Game:
    background_color = (0, 0, 0)
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
        pygame.key.set_repeat(self.key_delay, self.key_repeat)
        self.screen = pygame.display.set_mode(self.screen_resolution)

        # setup display and background color/size
        pygame.display.set_icon(pygame.image.load('graphics/icon.bmp'))
        pygame.display.set_caption('u can sav the world!')
        self.background = pygame.Surface(self.screen_resolution)
        self.background.fill(self.background_color)

        # declare levels
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
        self.town_level.add_npc(Friendly(10, 7))
        self.town_level.add_npc(Friendly(25, 5))
        self.town_level.add_npc(Friendly(43, 7))
        self.town_level.add_npc(Friendly(13, 32))
        self.town_level.add_npc(Friendly(23, 27))
        self.town_level.add_npc(Friendly(36, 29))

        # set enemies
        self.dungeon_1_level.add_npc(Enemy(4, 18))
        self.dungeon_1_level.add_npc(Enemy(4, 4))
        self.dungeon_1_level.add_npc(Enemy(32, 2))
        self.dungeon_1_level.add_npc(Enemy(32, 17))
        self.dungeon_1_level.add_npc(Enemy(32, 21))

        # initialize game to first level
        self.current_map = None
        self.current_level = self.town_level
        self.load_level(self.town_level)
        self.player = Player()

        # make the wall and floor class
        self.floor = []
        self.floor.append(load_image(os.path.join(graphics_dir, "floor_1.bmp")))
        self.floor.append(load_image(os.path.join(graphics_dir, "floor_2.bmp")))
        self.wall = []
        self.wall.append(load_image(os.path.join(graphics_dir, "wall_1.bmp")))
        self.wall.append(load_image(os.path.join(graphics_dir, "wall_2.bmp")))
        self.warp = load_image(os.path.join(graphics_dir, "warp.bmp"))

    # LOAD LEVEL
    # load the level passed in into memory
    def load_level(self, lev):
        if self.current_map is not None:
            self.current_map.clear()
        self.current_map = list(csv.reader(open(lev.level_path)))
        for i in range(len(self.current_map)):
            for j in range(len(self.current_map[0])):
                if self.current_map[i][j] == '_':  # set null
                    self.current_map[i][j] = -1
                elif self.current_map[i][j] == '.':  # set floors
                    self.current_map[i][j] = 1
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
        for a, b in lev.warp_list.items():
            warp_point = a.split(',')
            self.current_map[int(warp_point[1])][int(warp_point[0])] = 0

    # CONTROL TICK
    # this function will handle all input functions
    # returns false when game is ready to quit
    def control_tick(self):

        if joystick_count > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()

        pos_right = self.current_map[self.player.y][self.player.x + 1]
        pos_left = self.current_map[self.player.y][self.player.x - 1]
        pos_up = self.current_map[self.player.y - 1][self.player.x]
        pos_down = self.current_map[self.player.y + 1][self.player.x]

        while True:
            # improve performance by waiting to draw until new event is on event queue
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                return False

            if event.type == KEYDOWN:
                if event.key == K_RIGHT and (pos_right < 61):
                    self.player.x += 1
                    return True
                elif event.key == K_LEFT and (pos_left < 61):
                    self.player.x -= 1
                    return True
                elif event.key == K_UP and (pos_up < 61):
                    self.player.y -= 1
                    return True
                elif event.key == K_DOWN and (pos_down < 61):
                    self.player.y += 1
                    return True
                elif event.key == K_ESCAPE:
                    return False

            # xinput controls
            # need to implement repeat on hold down. no pygame methods available for this
            if event.type == JOYHATMOTION:
                hat = joystick.get_hat(0)
                if hat == (1, 0) and (pos_right < 61):
                    self.player.x += 1
                    return True
                if hat == (-1, 0) and (pos_left < 61):
                    self.player.x -= 1
                    return True
                if hat == (0, 1) and (pos_up < 61):
                    self.player.y -= 1
                    return True
                if hat == (0, -1) and (pos_down < 61):
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
                self.current_level = warp.new_level
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
                        self.screen.blit(self.floor[1], ((x - self.player.x + self.screen_x_buffer) * 32,
                                                      (y - self.player.y + self.screen_y_buffer) * 32))
                    elif self.current_map[y][x] > 0:
                        self.screen.blit(self.floor[0], ((x - self.player.x + self.screen_x_buffer) * 32,
                                                      (y - self.player.y + self.screen_y_buffer) * 32))
                    elif self.current_map[y][x] == 0:
                        self.screen.blit(self.warp, ((x - self.player.x + self.screen_x_buffer) * 32,
                                                     (y - self.player.y + self.screen_y_buffer) * 32))

        # draw enemies on the screen
        if len(self.current_level.npcs) > 0:
            for npc in self.current_level.npcs:
                if npc.x_pos in range(len(self.current_map[0])) and npc.y_pos in range(len(self.current_map)):
                    self.screen.blit(npc.image, ((npc.x_pos - self.player.x + self.screen_x_buffer) * 32,
                                                 (npc.y_pos - self.player.y + self.screen_y_buffer) * 32))

        # draw player in the center of the screen
        self.screen.blit(self.player.image, (self.screen_x_buffer * 32, self.screen_y_buffer * 32))
        pygame.display.flip()

    # main game loop
    def run(self):
        while 1:
            self.draw_tick()
            # return if control returns false
            if not self.control_tick():
                return


def main():
    new_game = Game()
    new_game.run()

    return


main()