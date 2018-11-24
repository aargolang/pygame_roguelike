from event import Event

class GameObj(object):
	event_moved = Event("event for object moved")

	def __init__(self, n):
		self.name = n

	def move(self):
		# move logic

		self.event_moved(self,"n")

class MapObj(object):

	def onObjMoved(self,sender,eventArgs):
		print("updating the position of " + str(sender.name))
		if eventArgs != None:
			print("event args is " + str(eventArgs))

if __name__ == '__main__':
	o = GameObj('harry')
	m = MapObj()

	o.event_moved += m.onObjMoved

	o.move()

