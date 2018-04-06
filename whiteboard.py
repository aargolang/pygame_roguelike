import csv

current_level = list(csv.reader(open('levels/test.csv')))

for i in range(len(self.current_level)):
    for j in range(len(self.current_level[0])):
        if self.current_level[i][j] == '_':              # set null
            self.current_level[i][j] = -1
        elif self.current_level[i][j] == '.':            # set floors
            self.current_level[i][j] = 0
        elif current_level[i][j] == ',':
            current_level[i][j] = 21
        elif current_level[i][j] == '`':
            current_level[i][j] = 41
        elif current_level[i][j] == '1':            # set walls
            current_level[i][j] = 61
        elif current_level[i][j] == '2':
            current_level[i][j] = 81
        elif current_level[i][j] == '3':
            current_level[i][j] = 101

for row in current_level:
    print(row)


