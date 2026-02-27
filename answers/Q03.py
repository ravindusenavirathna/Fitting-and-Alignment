import cv2
import numpy as np

points = []


def mouse_callback(event, x, y, flags, param):
    global points, img_display
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 4:
            points.append((x, y))
            print(f"Point {len(points)}: ({x}, {y})")
            cv2.circle(img_display, (x, y), 5, (0, 0, 255), -1)
            cv2.imshow("Image", img_display)
        if len(points) == 4:
            print("\nFour points selected. Press any key to continue.")


turf_img = cv2.imread("../assets/turf.jpg")
flag_img = cv2.imread("../assets/sri_lanka_flag.png")

img_display = turf_img.copy()
cv2.namedWindow("Image")
cv2.setMouseCallback("Image", mouse_callback)

print("Click 4 corners on the cricket turf.")
print("IMPORTANT: Click them in this order: Top-Left, Top-Right, Bottom-Right, Bottom-Left")
cv2.imshow("Image", img_display)

cv2.waitKey(0)
cv2.destroyAllWindows()

if len(points) != 4:
    print("You didn't select 4 points. Exiting program.")
    exit()

pts_dst = np.array(points, dtype=np.float32)

h, w, _ = flag_img.shape

pts_src = np.array([
    [0, 0],          # Top-Left
    [w - 1, 0],      # Top-Right
    [w - 1, h - 1],  # Bottom-Right
    [0, h - 1]       # Bottom-Left
], dtype=np.float32)

H, status = cv2.findHomography(pts_src, pts_dst)

warped_flag = cv2.warpPerspective(
    flag_img, H, (turf_img.shape[1], turf_img.shape[0]))

mask = np.ones((h, w, 3), dtype=np.uint8) * 255

warped_mask = cv2.warpPerspective(
    mask, H, (turf_img.shape[1], turf_img.shape[0]))

inverse_mask = cv2.bitwise_not(warped_mask)
turf_bg = cv2.bitwise_and(turf_img, inverse_mask)

opacity = 0.5

turf_roi = cv2.bitwise_and(turf_img, warped_mask)

blended_roi = cv2.addWeighted(warped_flag, opacity, turf_roi, 1 - opacity, 0)

final_result = cv2.add(turf_bg, blended_roi)

cv2.imshow("Superimposed Flag", final_result)
print("\nSuccess! Press any key to close the final image.")
cv2.waitKey(0)
cv2.destroyAllWindows()

cv2.imwrite("../results/superimposed_result.jpg", final_result)
print("Image saved as 'superimposed_result.jpg'")
