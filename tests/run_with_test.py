import cv2

from nti.vision.utils import get_test_images


def run_with_test_images(func):
    def wrapper():
        images = tuple(get_test_images())
        i = 0
        images_count = len(images)

        while True:
            img = images[i].copy()
            func(img)

            k = cv2.waitKey(0)
            if k == 27:
                break
            elif k == 97:  # a
                i = i - 1 if i > 0 else images_count - 1
            else:
                i = i + 1 if i < images_count - 1 else 0
    return wrapper
