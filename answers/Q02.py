import cv2
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

f_mm = 8.0
Z_mm = 720.0
pixel_pitch_mm = 0.0022
mm_per_pixel = (pixel_pitch_mm * Z_mm) / f_mm

img = cv2.imread("../assets/earrings.jpg")

img_annotated = img.copy()
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Threshold to isolate the shapes
_, thresh = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY_INV)

# Draw Bounding Boxes
contours, hierarchy = cv2.findContours(
    thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

for i, contour in enumerate(contours):
    if cv2.contourArea(contour) > 500:

        parent_idx = hierarchy[0][i][3]
        is_outer = (parent_idx == -1)
        label = "OUTER Box" if is_outer else "INNER Box"

        # Blue for Outer, Red for Inner
        box_color = (255, 0, 0) if is_outer else (0, 0, 255)

        bx, by, bw, bh = cv2.boundingRect(contour)

        real_width_mm = bw * mm_per_pixel

        print(f"{label}:")
        print(f"  - Pixel Width: {bw} px")
        print(f"  - Real Diameter: {real_width_mm:.2f} mm\n")

        cv2.rectangle(img_annotated, (bx, by),
                      (bx + bw, by + bh), box_color, 2)

        y_center = by + (bh // 2)
        cv2.line(img_annotated, (bx, y_center),
                 (bx + bw, y_center), box_color, 1)
        cv2.circle(img_annotated, (bx, y_center), 4, box_color, -1)
        cv2.circle(img_annotated, (bx + bw, y_center), 4, box_color, -1)

        cv2.putText(img_annotated, label, (bx, by - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color, 2)

img_annotated_rgb = cv2.cvtColor(img_annotated, cv2.COLOR_BGR2RGB)

height_px, width_px, _ = img_rgb.shape
total_width_mm = width_px * mm_per_pixel
total_height_mm = height_px * mm_per_pixel

fig, ax = plt.subplots(figsize=(10, 8))
ax.imshow(img_annotated_rgb, extent=[0, total_width_mm, total_height_mm, 0])

ax.xaxis.set_minor_locator(ticker.MultipleLocator(2))
ax.yaxis.set_minor_locator(ticker.MultipleLocator(2))

ax.grid(which='major', color='black', linestyle='-', linewidth=1.2, alpha=0.8)
ax.grid(which='minor', color='black', linestyle=':', linewidth=0.7, alpha=0.5)

ax.set_xlabel("Width (mm)", fontsize=12, fontweight='bold')
ax.set_ylabel("Height (mm)", fontsize=12, fontweight='bold')
ax.set_title("Earring Dimensions with Millimeter Grid",
             fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig("../results/earrings_bounding_boxes.png", dpi=300)
plt.show()
