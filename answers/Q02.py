# """
# IN4640 Assignment 2 - Question 2
# Estimating physical size of earrings from a camera image.

# Camera parameters:
#   - Focal length      : f  = 8 mm
#   - Pixel size        : p  = 2.2 µm = 0.0022 mm
#   - Image distance    : di = 720 mm  (lens to sensor)
#                         --> object distance via thin lens equation
# """

# import cv2
# import numpy as np
# import matplotlib.pyplot as plt
# import matplotlib.patches as patches

# # ─────────────────────────────────────────────
# # 1.  CAMERA / LENS PARAMETERS
# # ─────────────────────────────────────────────
# f_mm = 8          # focal length  (mm)
# do_mm = 720        # object distance, i.e. lens-to-earrings (mm)
# px_mm = 0.0022     # pixel pitch   (mm/pixel)

# # Thin-lens equation:  1/f = 1/do + 1/di  =>  di = f*do / (do - f)
# di_mm = (f_mm * do_mm) / (do_mm - f_mm)

# # Magnification  m = di / do
# magnification = di_mm / do_mm

# print("=" * 50)
# print("CAMERA MODEL")
# print("=" * 50)
# print(f"  Focal length       f  = {f_mm} mm")
# print(f"  Object distance    do = {do_mm} mm")
# print(f"  Image distance     di = {di_mm:.4f} mm")
# print(f"  Magnification      m  = {magnification:.4f}")
# print(f"  Pixel size         p  = {px_mm} mm")
# print()


# def pixels_to_mm(n_pixels):
#     """Convert a pixel measurement in the image to mm in the real world."""
#     image_size_mm = n_pixels * px_mm       # size on sensor (mm)
#     real_size_mm = image_size_mm / magnification
#     return real_size_mm


# # ─────────────────────────────────────────────
# # 2.  LOAD IMAGE
# # ─────────────────────────────────────────────
# IMG_PATH = "../assets/earrings.jpg"   # <-- change to your image filename

# img = cv2.imread(IMG_PATH)
# if img is None:
#     raise FileNotFoundError(f"Could not load '{IMG_PATH}'. "
#                             "Place the earring image in the same folder.")

# img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# h, w = gray.shape
# print(f"Image size: {w} × {h} pixels")

# # ─────────────────────────────────────────────
# # 3.  AUTOMATIC MEASUREMENT VIA CONTOUR DETECTION
# # ─────────────────────────────────────────────
# # Threshold to isolate the (gold) earrings against a white background
# _, thresh = cv2.threshold(gray, 230, 255, cv2.THRESH_BINARY_INV)

# # Morphological clean-up
# kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
# thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
# thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN,  kernel)

# # Find contours
# contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL,
#                                cv2.CHAIN_APPROX_SIMPLE)

# # Keep only the two largest contours (= the two earrings)
# contours = sorted(contours, key=cv2.contourArea, reverse=True)[:2]

# print("\n" + "=" * 50)
# print("AUTOMATIC CONTOUR-BASED MEASUREMENT")
# print("=" * 50)

# results = []
# img_annotated = img_rgb.copy()

# for i, cnt in enumerate(contours):
#     # Fit a bounding circle and an ellipse
#     (cx, cy), radius_px = cv2.minEnclosingCircle(cnt)
#     ellipse = cv2.fitEllipse(cnt)
#     (ex, ey), (ma, mi), angle = ellipse   # major & minor axes in pixels

#     # Convert pixel measurements to real-world mm
#     diameter_mm = pixels_to_mm(2 * radius_px)
#     major_mm = pixels_to_mm(ma)
#     minor_mm = pixels_to_mm(mi)

#     print(f"\n  Earring {i+1}  (centre ≈ ({cx:.0f}, {cy:.0f}) px)")
#     print(f"    Enclosing circle  radius = {radius_px:.1f} px  "
#           f"→ diameter = {diameter_mm:.2f} mm")
#     print(f"    Fitted ellipse    major  = {ma:.1f} px  → {major_mm:.2f} mm")
#     print(f"                      minor  = {mi:.1f} px  → {minor_mm:.2f} mm")

#     results.append(dict(cx=cx, cy=cy, radius_px=radius_px,
#                         diameter_mm=diameter_mm,
#                         major_mm=major_mm, minor_mm=minor_mm))

#     # Draw on image
#     cv2.circle(img_annotated,
#                (int(cx), int(cy)), int(radius_px), (255, 80, 0), 2)
#     cv2.putText(img_annotated,
#                 f"E{i+1}: {diameter_mm:.1f} mm",
#                 (int(cx - radius_px), int(cy - radius_px - 8)),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 80, 0), 2)

# # ─────────────────────────────────────────────
# # 4.  INTERACTIVE MANUAL MEASUREMENT (matplotlib)
# #     Click two points → get the real distance
# # ─────────────────────────────────────────────
# manual_points = []


# def on_click(event):
#     if event.inaxes and event.button == 1:
#         manual_points.append((event.xdata, event.ydata))
#         ax2.plot(event.xdata, event.ydata, 'r+', markersize=12, mew=2)
#         if len(manual_points) == 2:
#             p1, p2 = manual_points
#             dist_px = np.hypot(p2[0]-p1[0], p2[1]-p1[1])
#             dist_mm = pixels_to_mm(dist_px)
#             ax2.plot([p1[0], p2[0]], [p1[1], p2[1]], 'r-', lw=1.5)
#             ax2.set_title(f"Manual: {dist_px:.1f} px  →  {dist_mm:.2f} mm",
#                           color='red')
#             manual_points.clear()   # reset for next pair
#         fig2.canvas.draw()


# fig2, ax2 = plt.subplots(figsize=(7, 5))
# ax2.imshow(img_rgb)
# ax2.set_title("Click two points to measure a distance  (repeatable)")
# fig2.canvas.mpl_connect('button_press_event', on_click)

# # ─────────────────────────────────────────────
# # 5.  SUMMARY PLOT
# # ─────────────────────────────────────────────
# fig, axes = plt.subplots(1, 3, figsize=(15, 5))
# fig.suptitle("Earring Size Estimation", fontsize=14, fontweight='bold')

# axes[0].imshow(img_rgb)
# axes[0].set_title("Original Image")
# axes[0].axis('off')
# axes[1].imshow(thresh, cmap='gray')
# axes[1].set_title("Binary Mask")
# axes[1].axis('off')
# axes[2].imshow(img_annotated)
# axes[2].set_title("Detected Earrings")
# axes[2].axis('off')

# # Add a text summary box
# summary = "\n".join(
#     [f"Earring {i+1}: ⌀ ≈ {r['diameter_mm']:.1f} mm" for i,
#         r in enumerate(results)]
# )
# axes[2].text(5, h - 10, summary, color='white', fontsize=10,
#              va='bottom',
#              bbox=dict(boxstyle='round', facecolor='black', alpha=0.6))

# plt.tight_layout()
# plt.savefig("earring_size_result.png", dpi=150, bbox_inches='tight')
# print("\nSaved result image → earring_size_result.png")
# plt.show()   # also shows the interactive manual measurement window
