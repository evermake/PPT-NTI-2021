import cv2

from nti.vision.aruco import (
    detect_aruco,
    get_ordered_corners,
    remove_aruco_from_image,
    transform_image_by_field_corners
)
from tests.run_with_test import run_with_test_images


@run_with_test_images
def test(img):
    corners, ids = detect_aruco(img)

    cv2.aruco.drawDetectedMarkers(img, corners, ids, borderColor=(255, 255, 0))

    h, w = img.shape[:2]
    img_center = (w / 2, h / 2)

    ordered_corners = get_ordered_corners(corners, ids, img_center)

    wrapped = transform_image_by_field_corners(img, ordered_corners)

    painted = remove_aruco_from_image(img, corners)

    for corner in ordered_corners:
        cv2.circle(img, tuple(map(int, corner)), 1, (0, 50, 255), 2)

    cv2.imshow('Detected aruco', img)
    cv2.imshow('Wrapped', wrapped)
    cv2.imshow('Painted', painted)


if __name__ == '__main__':
    test()
