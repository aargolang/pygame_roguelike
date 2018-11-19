# pygame_roguelike
a simple roguelike made in python with PyGame

short:
I have no idea how far I plan to take this game. I imagine I will just keep working on it until either the game is limited by the language or the game is large enough that I feel it is somewhat complete.

Directions:

	Menu:
	the bracketed character will choose the selection

	Game:
	directional keys to move/attack/talk/trade/pay respects/not die/save the world

11/18/18: Yep, I broke the build. decided to take a look at this project and decided that there was much under the hood that needed to be improved. I took a shot at trying to fix it in one day but I bit off a little more than I could chew for one day. The project does not build at the moment but there are still many improvements:
> levels are stored as json files instead of csv files
> levels will have two layers map and object matrix. this will make all rendering and checking much simpler and faster than before. 
> game is now broken up into separate files. no more all-in-one file.

There is now less coupling across the board but there are still parts the need rethinking. Once the new system is running then I will focus on making the code scalable. 
