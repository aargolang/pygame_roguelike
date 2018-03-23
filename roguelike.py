import os
import pygame
import csv
from pygame.locals import *
from pygame.compat import geterror

# TODO
# - load maps from csv files
# - possibly reduce memory usage for large maps by only storing the walls
# - figure out how to load enemies into the levels
# - only render a new frame after user input to save processing time
# - make the player not able to walk through walls
# - clean up floor and wall graphics implementation

# set global varbarians to the source folder
# and subfolders
main_dir = os.path.split(os.path.abspath(__file__))[0]
graphics_dir = os.path.join(main_dir, 'graphics')
sound_dir = os.path.join(main_dir, 'sound')

# xinput settings
pygame.joystick.init()
joystick_count = pygame.joystick.get_count()


# the structure of levels will be determined by matricies with
# negative values being void and 0 and 1 being floor and wall respectively

test_map = list(csv.reader(open('levels/level_1.csv')))


def load_image(name, colorkey=None):
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


class Player(pygame.sprite.Sprite):                 # initialize
    onscreen_size = (32, 32)                        # global size on the screen
    start_x = 16                                   # global starting x pos
    start_y = 16                                   # global starting y pos

    def __init__(self):                             # player default constructor
        pygame.sprite.Sprite.__init__(self)         # initialize player as a default sprite
        self.image, self.rect = load_image(         # load player.bmp
            "player.bmp"
        )

        self.x = self.start_x                       # set starting x position
        self.y = self.start_y                       # set starting y position


class Game:
    bg_color = (0, 0, 0)                            # background filler color
    screen_resolution = (544, 544)                  # on screen window size
    grid_size = 1                                  # size of a size of the grid

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
        self.player = Player()                      # initialize a player
        self.floor = pygame.image.load(os.path.join(graphics_dir, "floor.bmp"))
        dimensions = (2 * self.floor.get_width(), 2 * self.floor.get_height())
        self.floor = pygame.transform.scale(self.floor, dimensions)

        self.wall = pygame.image.load(os.path.join(graphics_dir, "wall.bmp"))
        dimensions = (2 * self.wall.get_width(), 2 * self.wall.get_height())
        self.wall = pygame.transform.scale(self.wall, dimensions)

    # CONTROL TICK
    # this function will handle all input functions
    # returns false when game is ready to quit

    def control_tick(self):

        player = self.player
        grid_size = self.grid_size

        for event in pygame.event.get():
            if event.type == KEYDOWN:                   # key down controls
                if event.key == K_RIGHT and (test_map[player.y][player.x + 1] != '1'):
                    player.x += grid_size
                elif event.key == K_LEFT and (test_map[player.y][player.x - 1] != '1'):
                    player.x -= grid_size
                elif event.key == K_UP and (test_map[player.y - 1][player.x] != '1'):
                    player.y -= grid_size
                elif event.key == K_DOWN and (test_map[player.y + 1][player.x] != '1'):
                    player.y += grid_size
                elif event.key == K_ESCAPE:
                    return False

        # xinput controls
        if joystick_count > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            hat = joystick.get_hat(0)
            if hat == (1, 0):
                player.x += grid_size
            if hat == (-1, 0):
                player.x -= grid_size
            if hat == (0, 1):
                player.y -= grid_size
            if hat == (0, -1):
                player.y += grid_size

        return True

    # DRAW TICK
    # this function handles all of the rendering functionality
    # has no return value

    def draw_tick(self):
        self.screen.blit(self.background, (0, 0))

        # draw the test_map matrix
        for x in range(self.player.x - 8, self.player.x + 9):
            for y in range(self.player.y - 8, self.player.y + 9):
                if test_map[y][x] == '1':
                    self.screen.blit(self.wall, ((x - self.player.x + 8) * 32, (y - self.player.y + 8) * 32))
                elif test_map[y][x] == '0':
                    self.screen.blit(self.floor, ((x - self.player.x + 8) * 32, (y - self.player.y + 8) * 32))

        self.screen.blit(self.player.image, (
            8 * 32,
            8 * 32
        ))
        pygame.display.flip()

    def run(self):
        while 1:                                # main game loop
            if not self.control_tick():         # return if control returns false
                return

            self.draw_tick()


def main():
    new_game = Game()
    new_game.run()

    return


main()
