import cv2
import json
import numpy as np
from ultralytics import YOLO

class ZoneMonitor:
    def __init__(self, video_path, config_path):
        self.model = YOLO("yolo11n.pt")
        self.cap = cv2.VideoCapture(video_path)
        self.zone = self._load_zone(config_path)
        
    def _load_zone(self, path):
        with open(path, "r") as f:
            data = json.load(f)
        return np.array(data["points"], np.int32)

    def is_inside(self, point):
        # cv2.pointPolygonTest возвращает:
        # +1 (внутри), 0 (на границе), -1 (снаружи)
        return cv2.pointPolygonTest(self.zone, point, False) >= 0

    def run(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret: break

            # Отрисовка зоны
            cv2.polylines(frame, [self.zone], isClosed=True, color=(255, 255, 0), thickness=2)

            # Детекция (только класс 0 - person)
            results = self.model(frame, classes=[0], verbose=False)[0]

            for box in results.boxes:
                # Получаем координаты b-box: [x1, y1, x2, y2]
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                # Точка ног: центр по X, низ по Y
                feet_point = (int((x1 + x2) / 2), y2)
                
                # Проверка вхождения
                if self.is_inside(feet_point):
                    # Рисуем красный бокс, если в зоне
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.circle(frame, feet_point, 5, (0, 0, 255), -1)
                else:
                    # Обычный бокс
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            cv2.imshow("Security Monitor", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    monitor = ZoneMonitor("data/test.mp4", "restricted_zones.json")
    monitor.run()