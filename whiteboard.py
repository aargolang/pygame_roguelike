import pygame
import os
from pygame.locals import *
from pygame.compat import geterror


main_dir = os.path.split(os.path.abspath(__file__))[0]
graphics_dir = os.path.join(main_dir, 'graphics')

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.display.set_mode((100, 100))


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


class Player(pygame.sprite.Sprite):                 # initialize
    def __init__(self, init_x=0, init_y=0):             # player default constructor
        pygame.sprite.Sprite.__init__(self)         # initialize player as a default sprite
        self.image, self.rect = load_image_rect(                    # load player.bmp
            "player.png"
        )

        self.x = init_x                             # set starting x position
        self.y = init_y                             # set starting y position


def main():
    p1 = Player()

    grp = pygame.sprite.Group

    p1.rect.inflate(1, 1)

    grp.add(p1.image)




main()
