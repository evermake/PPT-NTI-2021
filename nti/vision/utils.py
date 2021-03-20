import os
import pathlib

import cv2


def get_test_images():
    path = pathlib.Path(__file__).parent.absolute()
    path = os.path.join(path, 'dataset/')
    for _, _, filenames in os.walk(path):
        for fn in filenames:
            yield cv2.imread(os.path.join(path, fn))
