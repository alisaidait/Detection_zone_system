import cv2
import json
import os
import numpy as np
from shapely.geometry import Polygon

def select_death_zone(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Ошибка: Не удалось открыть видео по пути {video_path}")
        return []
    
    # Пропускаем первые 30 кадров для лучшей видимости (чтобы не было черного экрана)
    cap.set(cv2.CAP_PROP_POS_FRAMES, 30)
    success, frame = cap.read()
    cap.release()

    if not success:
        print("Ошибка: Не удалось прочитать кадр из видео")
        return []
    
    window_name = "Nastroika Zony - ESC dlya vyhoda"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    # Делаем окно удобного размера (не обязательно на весь экран)
    cv2.resizeWindow(window_name, 1280, 720)
    
    display_frame = frame.copy()
    points = []
    
    def update_display():
        nonlocal display_frame
        display_frame = frame.copy()
        
        # Инструкции на экране
        instructions = [
            "LKM: Dobavit' tochku",
            "D: Udalit' poslednyuyu",
            "C: Ochistit' vse",
            "ENTER: Sohranit'",
            "ESC: Vyhod bez sohraneniya"
        ]
        
        for i, text in enumerate(instructions):
            cv2.putText(display_frame, text, (20, 40 + i*35), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        # Рисуем точки и линии
        if len(points) > 0:
            for i, (px, py) in enumerate(points):
                cv2.circle(display_frame, (px, py), 6, (0, 0, 255), -1)
                cv2.putText(display_frame, str(i+1), (px+10, py-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            if len(points) > 1:
                pts_array = np.array(points, np.int32)
                cv2.polylines(display_frame, [pts_array], False, (0, 255, 0), 2)
                
            if len(points) > 2:
                # Визуально замыкаем зону для предпросмотра
                cv2.line(display_frame, tuple(points[-1]), tuple(points[0]), (0, 255, 0), 1)
        
        cv2.imshow(window_name, display_frame)
    
    def mouse_callback(event, x, y, flags, param):
        nonlocal points
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            update_display()
    
    cv2.setMouseCallback(window_name, mouse_callback)
    update_display()
    
    while True:
        key = cv2.waitKey(0)
        
        if key == 13 or key == 10:  # ENTER
            if len(points) >= 3:
                break
            else:
                print("Nuzhno minimum 3 tochki!")
        elif key == ord('d') or key == ord('в'):  # D (en/ru)
            if points:
                points.pop()
                update_display()
        elif key == ord('c') or key == ord('с'):  # C (en/ru)
            points = []
            update_display()
        elif key == 27:  # ESC
            points = []
            break
    
    cv2.destroyAllWindows()
    return points

if __name__ == "__main__":
    # 1. Настройки путей
    VIDEO_PATH = "data/test.mp4" 
    JSON_PATH = "restricted_zones.json"

    # 2. Запуск выбора зоны
    print("Zapusk vybora zony...")
    polygon_points = select_death_zone(VIDEO_PATH)

    if polygon_points:
        print(f"Zona opredelena: {len(polygon_points)} tochek")
        
        # 3. Сохранение в JSON (чтобы использовать в основном коде)
        with open(JSON_PATH, "w") as f:
            json.dump({"points": polygon_points}, f)
        
        print(f"Nastroiki sohraneny v {JSON_PATH}")
    else:
        print("Vyborka otmenena ili nedostatochno tochek.")


