
import cv2
import json

VIDEO_PATH = "videos/parking_cctv.mp4"
OUTPUT_PATH = "spaces.json"

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    raise SystemExit("Error: Cannot open parking video.")

ret, frame = cap.read()

if not ret:
    cap.release()
    raise SystemExit("Error: Cannot read video.")

points = []
spaces = []
current_frame = frame.copy()


def mouse_callback(event, x, y, flags, param):
    global points, spaces

    if event == cv2.EVENT_LBUTTONDOWN:
        points.append([x, y])
        print(f"Point {len(points)}: ({x}, {y})")

        if len(points) == 4:
            spaces.append(points.copy())
            print(f"Parking space {len(spaces)} completed.")
            points.clear()


cv2.namedWindow("Parking Space Selection")
cv2.setMouseCallback("Parking Space Selection", mouse_callback)

print("""
CONTROLS
Click 4 corners of each parking space in order.
U = Undo last completed space
R = Reset all spaces
N = Next video frame
S = Save spaces
Q = Quit
""")

while True:
    display = current_frame.copy()

    for i, polygon in enumerate(spaces, start=1):
        pts = __import__("numpy").array(polygon, dtype="int32")
        cv2.polylines(display, [pts], True, (0, 255, 0), 2)

        center_x = int(sum(p[0] for p in polygon) / 4)
        center_y = int(sum(p[1] for p in polygon) / 4)

        cv2.putText(
            display, str(i), (center_x, center_y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
        )

    if points:
        for p in points:
            cv2.circle(display, tuple(p), 5, (0, 0, 255), -1)

        if len(points) > 1:
            for i in range(len(points) - 1):
                cv2.line(
                    display, tuple(points[i]), tuple(points[i + 1]),
                    (0, 0, 255), 2
                )

        cv2.putText(
            display, f"Corners: {len(points)}/4",
            (20, 35), cv2.FONT_HERSHEY_SIMPLEX,
            0.8, (0, 255, 255), 2
        )
    else:
        cv2.putText(
            display, f"Spaces: {len(spaces)}",
            (20, 35), cv2.FONT_HERSHEY_SIMPLEX,
            0.8, (0, 255, 255), 2
        )

    cv2.imshow("Parking Space Selection", display)
    key = cv2.waitKey(30) & 0xFF

    if key == ord("u"):
        if spaces:
            spaces.pop()
        points.clear()

    elif key == ord("r"):
        spaces.clear()
        points.clear()

    elif key == ord("n"):
        ret, next_frame = cap.read()
        if ret:
            current_frame = next_frame
            points.clear()

    elif key == ord("s"):
        if points:
            print("Finish the current space by selecting 4 corners first.")
            continue

        if not spaces:
            print("Select at least one parking space first.")
            continue

        data = {
            "video": VIDEO_PATH,
            "width": int(current_frame.shape[1]),
            "height": int(current_frame.shape[0]),
            "spaces": spaces
        }

        with open(OUTPUT_PATH, "w") as file:
            json.dump(data, file, indent=2)

        print(f"Saved {len(spaces)} spaces to {OUTPUT_PATH}")
        break

    elif key == ord("q") or key == 27:
        break

cap.release()
cv2.destroyAllWindows()
