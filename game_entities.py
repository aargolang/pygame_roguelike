import pygame
import roguelike

# my libraries
import game_engine

# CLASS chest
# object that will eventually have contentes
class Chest(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = game_engine.load_image('obj_chest.png')
        self.x = x_pos
        self.y = y_pos

    def update(self, player, level_map):
        self.x = self.x

# CLASS Player
# stores player location
# stores player image and rect
# TODO: add player stats when battle system is made
class Player(pygame.sprite.Sprite):                 # initialize
    def __init__(self, init_x, init_y):             # player default constructor
        pygame.sprite.Sprite.__init__(self)         # initialize player as a default sprite
        self.image = game_engine.load_image(                    # load player.bmp
            "player.png"
        )

        self.x = init_x                             # set starting x position
        self.y = init_y                             # set starting y position
        self.alignment = 'GOOD'
