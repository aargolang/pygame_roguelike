import pygame
import os
import sys
from pygame.compat import geterror

# my libraries
from game_NPCs import load_image

# CLASS chest
# object that will eventually have contentes
class Chest(pygame.sprite.Sprite):
    def getRef(self):
        return self

    def toDict(self):
        return { 'type':'chest', 'x_pos':self.x_pos, 'y_pos':self.y_pos }

    def __init__(self, json_obj):
        if type(json_obj) == dict:
            pygame.sprite.Sprite.__init__(self)
            self.image = load_image('obj_chest.png')
            self.x_pos = json_obj['x_pos']
            self.y_pos = json_obj['y_pos']
        else:
            raise Exception('non dictionary or json type provided')

    def update(self, player, level_map):
        self.x = self.x

# CLASS Player
# stores player location
# stores player image and rect
# TODO: add player stats when battle system is made
class Player(pygame.sprite.Sprite):                 # initialize
    def __init__(self, init_x, init_y):             # player default constructor
        pygame.sprite.Sprite.__init__(self)         # initialize player as a default sprite
        self.image = load_image(                    # load player.bmp
            "player.png"
        )

        self.x_pos = init_x                             # set starting x position
        self.y_pos = init_y                             # set starting y position
        self.alignment = 'GOOD'
