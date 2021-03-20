import cv2
import numpy as np

from nti.constants import *
from .aruco import detect_aruco, get_ordered_corners, transform_image_by_field_corners, remove_aruco_from_image
from .config import (
    HSV_RED_FILTER_1, HSV_RED_FILTER_2, HSV_GREEN_FILTER, HSV_BLUE_FILTER,
    ARCH_MIN_AREA, CYLINDER_MAX_PERIM_PER_APPROX, CUBE_MIN_PERIM_PER_APPROX, PYRAMID_MIN_AREA
)
from .contours import (
    fill_contour, get_filtered_contours, get_biggest_contours,
    get_real_contour_area, get_approx_num, get_contour_perimeter_per_approx
)
from .filters import apply_clahe_inpaint, fill_redundant_area, filter_hsv
from .planimetry import get_points_distance


def get_block_coordinates(img, cnt, field_corners, tiles_num=1):
    height = 500
    width = 600

    h, w = img.shape[:2]

    black = np.zeros((h, w))
    cv2.drawContours(black, [cnt], -1, 255, -1)

    black_with_block = transform_image_by_field_corners(black, field_corners)

    tiles = []

    for cell_x, y in enumerate(range(height - 50, -1, -50)):
        cell_x = 25 + cell_x * 50
        for cell_y, x in enumerate(range(width - 50, -1, -50)):
            cell_y = 25 + cell_y * 50
            segment = black_with_block[y:y + 50, x:x + 50]
            tiles.append(((cell_x, cell_y), segment.sum()))

    tiles.sort(reverse=True, key=lambda c: c[1])
    return [t[0] for t in tiles[:tiles_num]]


def get_block_marker_center(block_cnt, markers_thresh):
    h, w = markers_thresh.shape[:2]
    black = np.zeros((h, w), np.uint8)
    black = fill_contour(black, block_cnt)
    new_thresh = cv2.bitwise_and(black, markers_thresh)
    cntrs = get_filtered_contours(new_thresh, min_area=0.0)

    marker_cnt = get_biggest_contours(cntrs, 1)[0]

    matrix = cv2.moments(marker_cnt)
    cx = int(matrix['m10'] / matrix['m00'])
    cy = int(matrix['m01'] / matrix['m00'])

    return cx, cy


def get_point_conjectural_coordinate(pt, field_corners):
    height = 500
    width = 600

    pts2 = np.float32([[599, 499], [0, 499], [0, 0], [599, 0]])
    pts1 = []
    for corner in field_corners:
        pts1.append([corner[0], corner[1]])
    pts1 = np.float32(pts1)

    M = cv2.getPerspectiveTransform(pts1, pts2)

    # Calculate point coordinate after transformation
    px = (M[0][0] * pt[0] + M[0][1] * pt[1] + M[0][2]) / (
        (M[2][0] * pt[0] + M[2][1] * pt[1] + M[2][2]))
    py = (M[1][0] * pt[0] + M[1][1] * pt[1] + M[1][2]) / (
        (M[2][0] * pt[0] + M[2][1] * pt[1] + M[2][2]))

    pt = (px, py)

    tiles = []

    for cell_x, y in enumerate(range(height - 50, -1, -50)):
        cell_x = 25 + cell_x * 50
        for cell_y, x in enumerate(range(width - 50, -1, -50)):
            cell_y = 25 + cell_y * 50
            tiles.append(((cell_x, cell_y), get_points_distance((x + 25, y + 25), pt)))

    tiles.sort(key=lambda c: c[1])
    return tiles[0][0]


def get_blocks_list(img, debug=False):
    found_blocks = []

    h, w = img.shape[:2]

    img_center = (w / 2, h / 2)

    # - - - Find aruco - - -
    aruco_corners, aruco_ids = detect_aruco(img)
    field_corners = get_ordered_corners(aruco_corners, aruco_ids, img_center)

    # Apply CLAHE
    clahe = apply_clahe_inpaint(img)
    blur = cv2.medianBlur(clahe, 3)
    cropped = fill_redundant_area(blur)
    cropped = remove_aruco_from_image(cropped, aruco_corners)

    kernel = np.ones((3, 3), np.uint8)

    # - Find blue markers -

    blue_thresh = filter_hsv(cropped, (HSV_BLUE_FILTER,))
    blue_thresh = cv2.dilate(blue_thresh, kernel)

    # - - - Find blocks contours - - -

    red_thresh = filter_hsv(cropped, (HSV_RED_FILTER_1, HSV_RED_FILTER_2))
    red_thresh = cv2.dilate(red_thresh, kernel)
    red_thresh = cv2.erode(red_thresh, kernel)
    red_contours = get_filtered_contours(red_thresh)

    # First red blocks
    for red in red_contours:
        M = cv2.moments(red)
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
        area = get_real_contour_area(red)
        approx_len = get_approx_num(red)
        perim_per_approx = get_contour_perimeter_per_approx(red)

        if area >= ARCH_MIN_AREA:
            block_id = BLOCK_ARCH
        elif perim_per_approx <= CYLINDER_MAX_PERIM_PER_APPROX:
            # TODO: distinguish between a quarter and a cylinder
            # Cylinder / Quarter
            block_id = BLOCK_CYLINDER
        elif perim_per_approx >= CUBE_MIN_PERIM_PER_APPROX:
            block_id = BLOCK_CUBE
        else:
            block_id = BLOCK_QUARTER

        marker_center = get_block_marker_center(red, blue_thresh)

        if block_id == BLOCK_ARCH:
            marker_suggested_coordinate = get_point_conjectural_coordinate(marker_center, field_corners)
            p1, p2 = get_block_coordinates(img, red, field_corners, tiles_num=2)

            dist1 = get_points_distance(marker_suggested_coordinate, p1)
            dist2 = get_points_distance(marker_suggested_coordinate, p2)

            if dist1 <= dist2:
                block_coordinate = p1
                x1, y1 = p1
                x2, y2 = p2
            else:
                block_coordinate = p2
                x1, y1 = p2
                x2, y2 = p1

            # Detect rot ((x1, y1) - point with marker)
            if x1 == x2:
                if y1 > y2:
                    block_rot = 90
                else:
                    block_rot = 270
            else:  # y1 == y2
                if x1 < x2:
                    block_rot = 0
                else:
                    block_rot = 180

        elif block_id == BLOCK_QUARTER:
            block_coordinate = get_block_coordinates(img, red, field_corners)[0]
            # Detect rotation

            # Find contour rect center
            (rect_x, rect_y), _, _ = cv2.minAreaRect(red)

            if cy < rect_y:
                if cx > rect_x:
                    block_rot = 270
                else:
                    block_rot = 180
            else:  # cy < rect_y
                if cx > rect_x:
                    block_rot = 0
                else:
                    block_rot = 90

            if debug:
                cv2.circle(img, (cx, cy), 2, (0, 0, 255), 1)
                cv2.circle(img, (int(rect_x), int(rect_y)), 2, (0, 155, 255), 1)
        else:
            block_coordinate = get_block_coordinates(img, red, field_corners)[0]
            block_rot = 0

        if debug:
            cv2.circle(img, marker_center, 1, (255, 0, 255), 3)
            cv2.drawContours(img, [red], 0, (0, 255, 255), 1)
            cv2.putText(
                img,
                # str(get_contour_perimeter_per_approx(red)),
                BLOCK_NAMES[block_id],
                (cx, cy),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (255, 255, 0),
                1)

        found_blocks.append({
            'id': str(block_id),
            'x': str(block_coordinate[0]),
            'y': str(block_coordinate[1]),
            'z': '0',
            'rot': str(block_rot)
        })

    # And the same thing for green blocks
    green_thresh = filter_hsv(cropped, (HSV_GREEN_FILTER,))
    green_thresh = cv2.bitwise_or(blue_thresh, green_thresh)
    green_thresh = cv2.dilate(green_thresh, kernel)
    green_thresh = cv2.erode(green_thresh, kernel)
    green_contours = get_filtered_contours(green_thresh)

    for green in green_contours:
        M = cv2.moments(green)
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
        area = get_real_contour_area(green)

        if area >= PYRAMID_MIN_AREA:
            block_id = BLOCK_PYRAMID
        else:
            block_id = BLOCK_CONE

        block_coordinate = get_block_coordinates(img, green, field_corners)[0]

        if debug:
            marker_center = get_block_marker_center(green, blue_thresh)

            cv2.circle(img, marker_center, 1, (255, 0, 255), 3)
            cv2.drawContours(img, [green], 0, (50, 255, 0), 1)
            cv2.putText(img, BLOCK_NAMES[block_id], (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        found_blocks.append({
            'id': str(block_id),
            'x': str(block_coordinate[0]),
            'y': str(block_coordinate[1]),
            'z': '0',
            'rot': '0'
        })

    return found_blocks
