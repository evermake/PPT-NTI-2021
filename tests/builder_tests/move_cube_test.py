import json

import cv2

from nti.vision.blocks_detector import get_blocks_list
from nti.field import get_cell_coord
from nti.robot import Robot


img = cv2.imread('just_cube.jpg')
block = get_blocks_list(img)[0]

from_cell = get_cell_coord(
    block.get('x'),
    block.get('y'),
    0
)


with open('cube_test.json', 'r') as f:
    data = json.load(f)
block = data['objectsinmm'][0]
to_cell = get_cell_coord(
    block.get('x'),
    block.get('y'),
    0
)

from_cell = from_cell[:2]
to_cell = to_cell[:2]

r = Robot()
r.move_block(from_cell, to_cell)
r.move_to_origin()
r.export_as_code()
