import csv
import json

# my libraries
import game_engine
import game_entities
import game_NPCs

def load_json(file_name):
	with open(file_name) as infile:
		return json.load(infile)	

def save_json(file_name, data):
	with open(file_name, 'w') as outfile:
			json.dump(data, outfile, indent=4)

def convert_csv_to_json():
	json_obj = {}
	json_obj['name'] = 'town'
	json_obj['objects'] = [
		{"type":"warp", "next_level":"dungeon_1", "x_pos":17, "y_pos":18, "x_dest":25, "y_dest":19},
		{"type":"warp", "next_level":"dungeon_1", "x_pos":8, "y_pos":2, "x_dest":14, "y_dest":4},
		{"type":"warp", "next_level":"forest_1", "x_pos":2, "y_pos":30, "x_dest":46, "y_dest":17},
		{"type":"friendly", "x_pos":10, "y_pos":7},
		{"type":"friendly", "x_pos":25, "y_pos":5},
		{"type":"friendly", "x_pos":43, "y_pos":7},
		{"type":"friendly", "x_pos":13, "y_pos":32},
		{"type":"friendly", "x_pos":23, "y_pos":27},
		{"type":"friendly", "x_pos":36, "y_pos":29},
		{"type":"chest", "x_pos":7, "y_pos":4}
	]
	json_obj['map'] = list(csv.reader(open('levels/town.csv')))
	save_json('town.json',json_obj)

	json_obj = {}
	json_obj['name'] = 'dungeon_1'
	json_obj['objects'] = [
		{"type":"warp", "next_level":"town", "x_pos":24, "y_pos":19, "x_dest":17, "y_dest":19},
		{"type":"warp", "next_level":"town", "x_pos":13, "y_pos":4, "x_dest":8, "y_dest":1},
		{"type":"warp", "next_level":"dungeon_2", "x_pos":5, "y_pos":2, "x_dest":18, "y_dest":36},
		{"type":"enemy", "x_pos":4, "y_pos":18},
		{"type":"enemy", "x_pos":4, "y_pos":4},
		{"type":"enemy", "x_pos":32, "y_pos":2},
		{"type":"enemy", "x_pos":32, "y_pos":21}
	]
	json_obj['map'] = list(csv.reader(open('levels/dungeon_1.csv')))
	save_json('dungeon_1.json',json_obj)

	json_obj = {}
	json_obj['name'] = 'dungeon_2'
	json_obj['objects'] = [
		{"type":"warp", "next_level":"dungeon_1", "x_pos":35, "y_pos":18, "x_dest":5, "y_dest":1}
	]
	json_obj['map'] = list(csv.reader(open('levels/dungeon_2.csv')))
	save_json('dungeon_2.json',json_obj)

	json_obj = {}
	json_obj['name'] = 'forest_1'
	json_obj['objects'] = [
		{"type":"warp", "next_level":"town", "x_pos":45, "y_pos":17, "x_dest":1, "y_dest":30}
	]
	json_obj['map'] = list(csv.reader(open('levels/dungeon_2.csv')))
	save_json('forest_1.json',json_obj)

if __name__ == '__main__':
	l = game_engine.Level()
	l.loadLevel('town')
	l.loadLevel('dungeon_1')
	l.loadLevel('dungeon_2')
	l.loadLevel('forest_1')

	game = game_engine.Game()
	# game.run()
