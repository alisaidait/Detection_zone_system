import cv2
import json
import numpy as np
from ultralytics import YOLO
import time 
import os

class ZoneMonitor:
    def __init__(self, video_path, config_path):
        self.model = YOLO("yolo11n.pt")
        self.cap = cv2.VideoCapture(video_path)
        self.zone = self._load_zone(config_path)
        
        # Переменные для логики тревоги
        self.last_intrusion_time = 0 
        self.alarm_duration = 3.0  # 3 сек после последнего обнаружения выключаем

    def _load_zone(self, path):
        with open(path, "r") as f:
            data = json.load(f)
        return np.array(data["points"], np.int32)

    def is_inside(self, point):
        return cv2.pointPolygonTest(self.zone, point, False) >= 0

    def run(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret: break

            current_time = time.time()
            results = self.model(frame, classes=[0], verbose=False)[0]
            
            someone_in_zone = False # кто-то в зоне в текущем кадре

            for box in results.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                feet_point = (int((x1 + x2) / 2), y2)
                
                if self.is_inside(feet_point):
                    someone_in_zone = True
                    self.last_intrusion_time = current_time # Обновляем время последнего обнаружения
                    color = (0, 0, 255)
                    cv2.circle(frame, feet_point, 5, color, -1)
                else:
                    color = (0, 255, 0)
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Логика тревоги: если кто-то в зоне или не прошло 3 секунды с момента последнего обнаружения
            if someone_in_zone or (current_time - self.last_intrusion_time < self.alarm_duration and self.last_intrusion_time > 0):
                cv2.putText(frame, "ALARM!", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
                zone_color = (0, 0, 255) # Зона краснеет
            else:
                zone_color = (255, 255, 255) # Зона бирюзовая

            cv2.polylines(frame, [self.zone], isClosed=True, color=zone_color, thickness=2)

            cv2.imshow("Security Monitor", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    monitor = ZoneMonitor("data/test.mp4", "restricted_zones.json")
    monitor.run()