import cv2

from nti.vision.blocks_detector import get_blocks_list
from tests.run_with_test import run_with_test_images


@run_with_test_images
def test(img):
    from pprint import pprint

    pprint(get_blocks_list(img, debug=True))
    print('-------------------')

    cv2.imshow('Original', img)


if __name__ == '__main__':
    test()
