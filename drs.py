# drs_system_final.py

import cv2
import numpy as np

# === Configuration ===
VIDEO_PATH = "demo.mp4"  # Change this to your real input video
OUTPUT_PATH = "drs_final_demo.mp4"
FPS = 30

# === Load Video ===
cap = cv2.VideoCapture(VIDEO_PATH)
fps = int(cap.get(cv2.CAP_PROP_FPS)) or FPS
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
out = cv2.VideoWriter(OUTPUT_PATH, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

# === Ball Path (example points) ===
# Replace this with actual detection/tracking logic
ball_path = [
    (width//2 - 100 + i*10, 100 + i*12) for i in range(15)
]

# === Zones Calculation ===
stump_width = width // 12
center = width // 2
leg = (center - stump_width*2, center - stump_width)
middle = (center - stump_width, center + stump_width)
off = (center + stump_width, center + stump_width*2)

def get_zone(x):
    if leg[0] <= x <= leg[1]:
        return "OUTSIDE LEG"
    elif middle[0] <= x <= middle[1]:
        return "IN-LINE"
    elif off[0] <= x <= off[1]:
        return "OUTSIDE OFF"
    return "UNKNOWN"

# === Pitch and Impact Point ===
def get_pitch_point(path):
    for i in range(1, len(path) - 1):
        if path[i-1][1] > path[i][1] < path[i+1][1]:
            return i, path[i]
    return 5, path[5]

pitch_idx, pitch_point = get_pitch_point(ball_path)
impact_idx = int(len(ball_path) * 0.7)
impact_point = ball_path[impact_idx]

pitch_zone = get_zone(pitch_point[0])
impact_zone = get_zone(impact_point[0])
decision = "OUT" if (pitch_zone == "IN-LINE" and impact_zone == "IN-LINE") else "NOT OUT"

# === Frame Index Setup ===
frame_idx = 0
pitch_frame = pitch_idx + 3
impact_frame = impact_idx + 5
decision_frame = impact_idx + 12

# === Drawing Colors ===
white = (255, 255, 255)
red = (0, 0, 255)
green = (0, 255, 0)
blue = (255, 0, 0)
yellow = (0, 255, 255)

# === Process Video ===
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Draw center line
    cv2.line(frame, (center, 0), (center, height), white, 2)

    # Draw ball trajectory
    for i in range(min(frame_idx + 1, len(ball_path))):
        cv2.circle(frame, ball_path[i], 5, yellow, -1)

    # Overlays
    if frame_idx >= pitch_frame:
        cv2.putText(frame, f"PITCHING: {pitch_zone}", (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, red, 3)
    if frame_idx >= impact_frame:
        cv2.putText(frame, f"IMPACT: {impact_zone}", (40, 120), cv2.FONT_HERSHEY_SIMPLEX, 1.2, blue, 3)
    if frame_idx >= impact_frame + 4:
        cv2.putText(frame, f"WICKETS: {'HITTING' if decision == 'OUT' else 'MISSING'}", (40, 180), cv2.FONT_HERSHEY_SIMPLEX, 1.2, green, 3)
    if frame_idx >= decision_frame:
        cv2.putText(frame, f"DECISION: {decision}", (40, 260), cv2.FONT_HERSHEY_SIMPLEX, 1.6, red if decision == "OUT" else green, 4)

    out.write(frame)
    frame_idx += 1

cap.release()
out.release()
print(f"✅ Final DRS video saved: {OUTPUT_PATH}")
