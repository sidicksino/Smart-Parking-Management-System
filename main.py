
import cv2

VIDEO_PATH = "videos/carPark.mp4"

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    print("Error: Cannot open video.")
    raise SystemExit(1)

print("Video opened successfully!")
print("Width:", int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)))
print("Height:", int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
print("FPS:", cap.get(cv2.CAP_PROP_FPS))

while True:
    ret, frame = cap.read()

    if not ret:
        break

    cv2.imshow("Smart Parking System", frame)

    if cv2.waitKey(25) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
