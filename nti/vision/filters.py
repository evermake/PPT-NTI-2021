import cv2
import numpy as np


def apply_clahe_inpaint(img):
    clahe = cv2.createCLAHE(2.0, (8, 8))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = clahe.apply(gray)
    mask = cv2.threshold(clahe, 220, 255, cv2.THRESH_BINARY)[1]
    return cv2.inpaint(img, mask, 0.1, cv2.INPAINT_NS)


def fill_redundant_area(img, color=(0, 0, 0)):
    img = img.copy()

    h, w = img.shape[:2]

    offset_top = 5
    offset_right = 33
    offset_bottom = 10
    offset_left = 50

    img[:offset_top] = np.full((w, 3), np.array(color))
    img[h - offset_bottom:] = np.full((w, 3), np.array(color))
    img[:, :offset_left] = np.full((offset_left, 3), np.array(color))
    img[:, w - offset_right:] = np.full((offset_right, 3), np.array(color))

    return img


def filter_hsv(img, filters):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    mask = np.zeros(img.shape[:2], np.uint8)
    for h, s, v in filters:
        low = np.array([h[0], s[0], v[0]])
        high = np.array([h[1], s[1], v[1]])
        mask = cv2.bitwise_or(mask, cv2.inRange(hsv, low, high))

    return mask
