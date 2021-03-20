import cv2

from .config import (
    CONTOUR_THRESHOLD_AREA, REAL_IMG_CENTER, MAX_DISTANCE_FROM_CENTER
)
from .planimetry import get_points_distance


def get_filtered_contours(src, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE, min_area=CONTOUR_THRESHOLD_AREA):
    cntrs, _ = cv2.findContours(src, mode, method)
    filtered = []

    for cnt in cntrs:
        if cv2.contourArea(cnt) >= min_area:
            filtered.append(cnt)

    return filtered


def get_contour_center_mass(cnt):
    M = cv2.moments(cnt)
    cx = int(M['m10'] / M['m00'])
    cy = int(M['m01'] / M['m00'])
    return cx, cy


def get_approx_num(cnt):
    peri = cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, 0.001 * peri, True)
    return len(approx)


def get_contour_perimeter_per_approx(cnt):
    peri = cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, 0.0015 * peri, True)
    return round(peri / len(approx), 4)


def get_real_contour_area(cnt):
    img_center = REAL_IMG_CENTER
    matrix = cv2.moments(cnt)
    cx = int(matrix['m10'] / matrix['m00'])
    cy = int(matrix['m01'] / matrix['m00'])
    area = matrix['m00']
    distance_to_center = get_points_distance((cx, cy), img_center)
    mx = MAX_DISTANCE_FROM_CENTER

    k = ((mx - distance_to_center) + 4 * mx) / (5 * mx)
    k = 1.0 if k >= 1.0 else k

    return round(area * k, 2)


def get_biggest_contours(cntrs, num):
    cntrs = sorted(cntrs, reverse=True, key=lambda c: get_real_contour_area(c))
    return cntrs[:num]


def fill_contour(img, cnt):
    img = img.copy()
    hull = cv2.convexHull(cnt)
    cv2.drawContours(img, [hull], 0, 255, -1)
    return img
