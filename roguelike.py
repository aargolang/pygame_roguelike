import os
import pygame
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

# the structure of levels will be determined by matricies with
# negative values being void and 0 and 1 being floor and wall respectively
test_map = [[1, 1, 1, 1, 1, 1, 1, -1, -1, -1],
            [1, 0, 0, 0, 0, 0, 1, -1, -1, -1],
            [1, 0, 0, 0, 0, 0, 1, -1, -1, -1],
            [1, 0, 0, 0, 0, 0, 1, -1, -1, -1],
            [1, 0, 0, 0, 0, 0, 1, -1, -1, -1],
            [1, 0, 0, 0, 0, 0, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1, -1, -1, -1],
            [1, 1, 1, 1, 1, 1, 1, -1, -1, -1]]


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
    start_x = 64                                    # global starting x pos
    start_y = 128                                   # global starting y pos

    def __init__(self):                             # player default constructor
        pygame.sprite.Sprite.__init__(self)         # initialize player as a default sprite
        self.image, self.rect = load_image(         # load player.bmp
            "player.bmp"
        )

        self.x = self.start_x                       # set starting x position
        self.y = self.start_y                       # set starting y position


class Game:
    bg_color = (0, 0, 0)                            # background filler color
    screen_resolution = (640, 480)                  # on screen window size
    grid_size = 32                                  # size of a size of the grid

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
                if event.key == K_RIGHT:
                    player.x += grid_size
                elif event.key == K_LEFT:
                    player.x -= grid_size
                elif event.key == K_UP:
                    player.y -= grid_size
                elif event.key == K_DOWN:
                    player.y += grid_size
                elif event.key == K_ESCAPE:
                    return False

        return True

    # DRAW TICK
    # this function handles all of the rendering functionality
    # has no return value

    def draw_tick(self):
        self.screen.blit(self.background, (0, 0))

        # draw the test_map matrix
        for x in range(len(test_map)):
            for y in range(len(test_map)):
                if test_map[y][x] == 1:
                    self.screen.blit(self.wall, (x * 32, y * 32))
                elif test_map[y][x] == 0:
                    self.screen.blit(self.floor, (x * 32, y * 32))

        self.screen.blit(self.player.image, (
            self.player.x,
            self.player.y
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
