
import cv2
import json
import numpy as np

JSON_PATH = "spaces.json"

# Initial threshold; we will tune it using your video.
EDGE_THRESHOLD = 0.065

with open(JSON_PATH, "r") as file:
    data = json.load(file)

VIDEO_PATH = data.get("video", "videos/parking.mp4")
spaces = data["spaces"]

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    raise SystemExit(f"Cannot open video: {VIDEO_PATH}")

print(f"Video: {VIDEO_PATH}")
print(f"Parking spaces: {len(spaces)}")
print("Press Q to quit.")

while True:
    ret, frame = cap.read()

    if not ret:
        # Restart the video when it reaches the end.
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(gray, 60, 150)

    occupied_count = 0
    available_count = 0

    for index, space in enumerate(spaces):
        polygon = np.array(space, dtype=np.int32)

        # Create a mask for this parking space.
        mask = np.zeros(gray.shape, dtype=np.uint8)
        cv2.fillPoly(mask, [polygon], 255)

        # Remove boundary lines to reduce false detections.
        mask = cv2.erode(
            mask,
            np.ones((5, 5), dtype=np.uint8),
            iterations=2
        )

        area = cv2.countNonZero(mask)

        if area == 0:
            continue

        # Measure the number of edges inside the space.
        edge_pixels = cv2.countNonZero(
            cv2.bitwise_and(edges, edges, mask=mask)
        )

        edge_ratio = edge_pixels / area

        # Basic heuristic: vehicles often create more edges
        # than empty pavement. This needs testing and tuning.
        occupied = edge_ratio > EDGE_THRESHOLD

        if occupied:
            occupied_count += 1
            color = (0, 0, 255)       # Red = occupied
            status = "OCCUPIED"
        else:
            available_count += 1
            color = (0, 255, 0)       # Green = available
            status = "AVAILABLE"

        cv2.polylines(
            frame, [polygon], True, color, 3
        )

        center = np.mean(polygon, axis=0).astype(int)
        x, y = center

        cv2.putText(
            frame,
            str(index + 1),
            (x - 10, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2
        )

    # Display the live parking statistics.
    cv2.rectangle(frame, (15, 15), (510, 125), (25, 25, 25), -1)

    cv2.putText(
        frame,
        f"Total spaces: {len(spaces)}",
        (30, 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"Available: {available_count}",
        (30, 78),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"Occupied: {occupied_count}",
        (30, 110),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 255),
        2
    )

    cv2.imshow("Smart Parking Management System", frame)

    if cv2.waitKey(25) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
