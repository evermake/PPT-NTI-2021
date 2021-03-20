import json

import cv2

from nti.vision.blocks_detector import get_blocks_list
from nti.builder import build_building

IMAGE_NAME = 'preview.jpg'
BUILDING_FILE_NAME = 'task.json'

img = cv2.imread(IMAGE_NAME)
initial_blocks = get_blocks_list(img)

with open(BUILDING_FILE_NAME, 'r') as f:
    data = json.load(f)
    required_blocks = data['objectsinmm']

build_building(initial_blocks, required_blocks)
