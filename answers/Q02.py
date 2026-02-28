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

boxes = {}
for i, contour in enumerate(contours):
    boxes[i] = cv2.boundingRect(contour)

table_data = []
measured_outer = False
measured_inner = False

for i, contour in enumerate(contours):
    if cv2.contourArea(contour) > 500:

        parent_idx = hierarchy[0][i][3]
        is_outer = (parent_idx == -1)
        label = "OUTER Box" if is_outer else "INNER Box"
        table_label = "OUTER" if is_outer else "INNER"

        # Blue for Outer, Red for Inner
        box_color = (255, 0, 0) if is_outer else (0, 0, 255)

        bx, by, bw, bh = boxes[i]

        if not is_outer and parent_idx in boxes:
            p_bx, p_by, p_bw, p_bh = boxes[parent_idx]
            original_bottom = by + bh

            by = p_by  # Make the inner top point the exact same as the outer top point
            bh = original_bottom - by  # Recalculate the height based on the new top

        if is_outer and not measured_outer:
            real_w_mm = bw * mm_per_pixel
            real_h_mm = bh * mm_per_pixel
            table_data.append(
                [table_label, f"{bw}", f"{real_w_mm:.2f}", f"{bh}", f"{real_h_mm:.2f}"])
            measured_outer = True

        elif not is_outer and not measured_inner:
            real_w_mm = bw * mm_per_pixel
            real_h_mm = bh * mm_per_pixel
            table_data.append(
                [table_label, f"{bw}", f"{real_w_mm:.2f}", f"{bh}", f"{real_h_mm:.2f}"])
            measured_inner = True

        cv2.rectangle(img_annotated, (bx, by),
                      (bx + bw, by + bh), box_color, 2)

        y_center = by + (bh // 2)
        cv2.line(img_annotated, (bx, y_center),
                 (bx + bw, y_center), box_color, 1)
        cv2.circle(img_annotated, (bx, y_center), 4, box_color, -1)
        cv2.circle(img_annotated, (bx + bw, y_center), 4, box_color, -1)

        x_center = bx + (bw // 2)
        cv2.line(img_annotated, (x_center, by),
                 (x_center, by + bh), box_color, 1)
        cv2.circle(img_annotated, (x_center, by), 4, box_color, -1)
        cv2.circle(img_annotated, (x_center, by + bh), 4, box_color, -1)

img_annotated_rgb = cv2.cvtColor(img_annotated, cv2.COLOR_BGR2RGB)

height_px, width_px, _ = img_rgb.shape
total_width_mm = width_px * mm_per_pixel
total_height_mm = height_px * mm_per_pixel

fig, (ax_img, ax_table) = plt.subplots(nrows=2, ncols=1,
                                       figsize=(10, 9), gridspec_kw={'height_ratios': [5, 1]})

ax_img.imshow(img_annotated_rgb, extent=[
              0, total_width_mm, total_height_mm, 0])

ax_img.xaxis.set_major_locator(ticker.MultipleLocator(10))
ax_img.yaxis.set_major_locator(ticker.MultipleLocator(10))
ax_img.xaxis.set_minor_locator(ticker.MultipleLocator(2))
ax_img.yaxis.set_minor_locator(ticker.MultipleLocator(2))

ax_img.grid(which='major', color='black',
            linestyle='-', linewidth=1.2, alpha=0.8)
ax_img.grid(which='minor', color='black',
            linestyle=':', linewidth=0.7, alpha=0.5)

ax_img.set_xlabel("Width (mm)", fontsize=12, fontweight='bold')
ax_img.set_ylabel("Height (mm)", fontsize=12, fontweight='bold')
ax_img.set_title("Earring Dimensions with Millimeter Grid",
                 fontsize=14, fontweight='bold')

ax_table.axis('off')
col_labels = ["Type", "Width (px)", "Width (mm)", "Height (px)", "Height (mm)"]
table = ax_table.table(cellText=table_data,
                       colLabels=col_labels, loc='center', cellLoc='center')
table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1, 1.8)

for (row, col), cell in table.get_celld().items():
    cell.set_edgecolor('black')
    if row == 0:
        cell.set_text_props(weight='bold', color='white')
        cell.set_facecolor('#333333')
    else:
        cell.set_facecolor('#ffffff')

plt.tight_layout()
plt.savefig("../results/earrings_bounding_boxes.png", dpi=300)
plt.show()
