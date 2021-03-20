import cv2
import numpy as np

from .planimetry import get_points_distance
from .contours import get_contour_center_mass


def detect_aruco(img):
    img = cv2.GaussianBlur(img, (3, 3), 0)
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters_create()
    parameters.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
    corners, ids, rejected = cv2.aruco.detectMarkers(img, dictionary, parameters=parameters)

    if len(corners) == 3:
        required_ids = {0, 1, 2, 3}
        found_ids = set(ids.flat)
        fourth_id = list(required_ids.difference(found_ids))[0]

        candidates = []
        for i in range(len(rejected)):
            rej = rejected[i]
            candidates.append((i, get_contour_center_mass(rej)))

        if fourth_id == 0:
            candidates.sort(key=lambda c: get_points_distance(c[1], (639, 479)))
        elif fourth_id == 1:
            candidates.sort(key=lambda c: get_points_distance(c[1], (0, 479)))
        elif fourth_id == 2:
            candidates.sort(key=lambda c: get_points_distance(c[1], (0, 0)))
        else:
            candidates.sort(key=lambda c: get_points_distance(c[1], (639, 0)))

        candidate = rejected[candidates[0][0]]
        fourth_marker = np.array([candidate], dtype=np.float32)

        corners = np.concatenate((corners, fourth_marker))
        ids = np.concatenate((ids, np.array([[fourth_id]])))

    return corners, ids


def get_ordered_corners(corners, ids, img_center):
    found_corners = []
    for id_, corners_bunch in zip(ids, corners):
        id_ = int(id_[0])
        corners_bunch = corners_bunch[0]

        found_corners.append((id_, min(
            corners_bunch,
            key=lambda c: get_points_distance(c, img_center)
        )))

    return [c[1] for c in sorted(found_corners, key=lambda c: c[0])]


def transform_image_by_field_corners(img, corners):
    cols, rows = 600, 500

    pts2 = np.float32([[599, 499], [0, 499], [0, 0], [599, 0]])
    pts1 = []
    for corner in corners:
        pts1.append([corner[0], corner[1]])
    pts1 = np.float32(pts1)

    M = cv2.getPerspectiveTransform(pts1, pts2)
    return cv2.warpPerspective(img, M, (cols, rows))


def remove_aruco_from_image(img, corners, color=(0, 0, 0)):
    """Paint over the aruco markers with the given color."""
    out = img.copy()

    for corner_points in corners:
        points = np.array(corner_points, np.int32)
        points = points.reshape((-1, 1, 2))
        cv2.fillPoly(out, [points], color)

    return out
