import pygame
from event import Event
import os

from pygame.compat import geterror

# my libraries
main_dir = os.path.split(os.path.abspath(__file__))[0]
graphics_dir = os.path.join(main_dir, 'graphics')
sound_dir = os.path.join(main_dir, 'sound')
level_dir = os.path.join(main_dir, 'levels')

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

# CLASS Friendly
# npcs that will be shopkeepers, random encounters, any npc that dosnt try to rob you
class Friendly(pygame.sprite.Sprite):
    def getRef(self):
        return self

    def toDict(self):
        return { 'type':'friendly', 'x_pos':self.x_pos, 'y_pos':self.y_pos }

    def __init__(self, json_obj):
        if type(json_obj) == dict:
            pygame.sprite.Sprite.__init__(self)
            self.image = load_image('friendly.png')
            self.x_pos = json_obj['x_pos']
            self.y_pos = json_obj['y_pos']
            self.agro = False
            self.alignment = 'GOOD'
        else:
            raise Exception('non dictionary or json type provided')

    def update(self, player, level_map):
        sight_distance = 2
        x_dif = self.x - player.x
        y_dif = self.y - player.y

        # TODO remove this placeholder code
        # placeholder player detection code
        if abs(x_dif) <= sight_distance and abs(y_dif) <= sight_distance:
            if player.alignment is 'BAD':
                # print('enemy agro')
                self.agro = True
        
        if self.agro is True:
            if abs(x_dif) < abs(y_dif):
                if y_dif > 0:
                    print('go up')
                    self.y -= 1
                else:
                    print('go down')
                    self.y += 1
            else:
                if x_dif < 0:
                    print('go right')
                    self.x += 1
                else:
                    print('go left')
                    self.x -= 1

# CLASS Enemy
# any NPC that IS going to try to rob you
class Enemy(pygame.sprite.Sprite):
    moved_event = Event("event that happens after movement")
    def getRef(self):
        return self

    def toDict(self):
        return { 'type':'enemy', 'x_pos':self.x_pos, 'y_pos':self.y_pos }

    def __init__(self, json_obj):
        if type(json_obj) == dict:
            pygame.sprite.Sprite.__init__(self)
            self.image = load_image('enemy.png')
            self.x_pos = json_obj['x_pos']
            self.y_pos = json_obj['y_pos']
            self.agro = False
            self.alignment = 'BAD'
        else:
            raise Exception('non dictionary or json type provided')

    def move(self, direction):
        
        if type(direction) == str:
            previous_position = (self.x_pos, self.y_pos)
            if direction[0].lower() == 'n':
                self.x_pos -= 1
            elif direction[0].lower() == 's':
                self.x_pos += 1
            elif direction[0].lower() == 'e':
                self.y_pos += 1
            elif direction[0].lower() == 'w':
                self.y_pos -= 1

            self.moved_event(self,previous_position)
        else:
            raise Exception('direction not of type string as needed')

    def update(self, player, level_map):
        sight_distance = 6
        x_dif = player.x - self.x
        if x_dif != 0:
            x_sign = int(x_dif/abs(x_dif))
        else:
            x_sign = 0
        y_dif = player.y - self.y
        if y_dif != 0:
            y_sign = int(y_dif/abs(y_dif))
        else:
            y_sign = 0

        # TODO remove this placeholder code
        # placeholder player detection code
        if abs(x_dif) <= sight_distance and abs(y_dif) <= sight_distance:
            if player.alignment is 'GOOD':
                # print('enemy agro')
                self.agro = True

        # basic enemy pathing
        # TODO: this might have a better solution that just being a forest of 'if' statements
        if self.agro is True:
            if abs(x_dif) > abs(y_dif):
                # if player is closer in the x dimension
                if level_map[self.y][self.x + x_sign] < 61:
                    # and there is no wall in that x direction,
                    if abs(x_dif) > 1:
                        # and the player is not next them in the x directioN
                        self.x += x_sign
                        # move in that direction
                elif level_map[self.y + y_sign][self.x] < 61:
                    # if there is a wall in the closer x direction,
                    if abs(y_dif) > 1:
                        # and the player is not next them in the y direction
                        self.y += y_sign
                        # move in the closer y direction
            elif abs(x_dif) <= abs(y_dif):
                # if player is closer in the y dimension
                if level_map[self.y + y_sign][self.x] < 61:
                    # and there is no wall in that y direction
                    if abs(y_dif) > 1:
                        # and the player is not next to them in the y direction
                        self.y += y_sign
                        # move in the closer y direction
                elif level_map[self.y][self.x + x_sign] < 61:
                    # if there is a wall in the closer y direction
                    if abs(x_dif) > 1:
                        # and the player is not next to them in the x direction
                        self.x += x_sign
                        # move in the closer x direction
