import json

from nti.field import Field


with open('test.json', 'r') as f:
    data = json.load(f)
    blocks = data['objectsinmm']
    f = Field(blocks)

print(f.get_occupied_cells())

for y in range(11, -1, -1):
    row = []
    for x in range(10):
        row.append(str(f.get_cell_height(x, y)))
    for s in row:
        print(s.center(5), end='')
    print('\n')
