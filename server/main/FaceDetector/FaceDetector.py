import os
import cv2
import numpy as np
import uuid

from server.settings import BASE_DIR

class FaceDetector:
    # Здесь другие XML файлы можно посмотреть и найти
    # https://github.com/anaustinbeing/haar-cascade-files/tree/master
    def __init__(self, cascade_path_face='haarcascade_frontalface_default.xml',
                 cascade_path_mouth='haarcascade_mcs_mouth.xml', cascade_path_eye='haarcascade_eye.xml'):
        # Определение лица
        self.face_cascade_path = os.path.join(BASE_DIR, 'main', 'FaceDetector', cascade_path_face)
        if not os.path.isfile(self.face_cascade_path):
            raise FileNotFoundError(f"Файл каскада лица '{self.face_cascade_path}' не найден.")
        self.face_cascade = cv2.CascadeClassifier(self.face_cascade_path)

        # Определение рта
        self.mouth_cascade_path = os.path.join(BASE_DIR, 'main', 'FaceDetector', cascade_path_mouth)
        if not os.path.isfile(self.mouth_cascade_path):
            raise FileNotFoundError(f"Файл каскада рта '{self.mouth_cascade_path}' не найден.")
        self.mouth_cascade = cv2.CascadeClassifier(self.mouth_cascade_path)

        # Определение глаза
        self.eye_cascade_path = os.path.join(BASE_DIR, 'main', 'FaceDetector', cascade_path_eye)
        if not os.path.isfile(self.eye_cascade_path):
            raise FileNotFoundError(f"Файл каскада глаз '{self.eye_cascade_path}' не найден.")
        self.eye_cascade = cv2.CascadeClassifier(self.eye_cascade_path)

    # Определение лица в кадре
    def detect_faces(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=5)
        return faces

    # Определение глаза в кадре
    def detect_eyes(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        eyes = self.eye_cascade.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=8)
        eye_centers = []
        for (ex, ey, ew, eh) in eyes:
            eye_center_x = ex + ew // 2
            eye_center_y = ey + eh // 2
            eye_centers.append((eye_center_x, eye_center_y))
        return eye_centers

    # Определение области рта в кадре
    def detect_mouth(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mouths = self.mouth_cascade.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=8)
        mouth_centers = []
        for (mx, my, mw, mh) in mouths:
            mouth_center_x = mx + mw // 2
            mouth_center_y = my + mh // 2
            mouth_centers.append((mouth_center_x, mouth_center_y))
        return mouth_centers

    # Определение плача человека в кадре
    def detect_crying(self, frame, faces):
        for (x, y, w, h) in faces:
            roi_gray = frame[y:y + h, x:x + w]
            eyes = self.eye_cascade.detectMultiScale(roi_gray)
            # Если не обнаружено глаз, считаем, что человек плачет
            if len(eyes) == 0: return True
        return False


class CameraAnalyzer:
    def __init__(self):
        self.face_detector = FaceDetector()
        # Сглаживание, чтобы рамка и текст не дергались
        self.smoothed_x = None
        self.smoothed_y = None

    def smooth_values(self, x, y, smoothing_factor=0.5):
        if smoothing_factor >= 1.0: ValueError("Сглаживание должно быть меньше 1.0")
        if self.smoothed_x is None or self.smoothed_y is None:
            self.smoothed_x = x
            self.smoothed_y = y
        else:
            self.smoothed_x = smoothing_factor * self.smoothed_x + (1 - smoothing_factor) * x
            self.smoothed_y = smoothing_factor * self.smoothed_y + (1 - smoothing_factor) * y
        return int(self.smoothed_x), int(self.smoothed_y)

    def annotate_frame(self, frame, faces, eyes, mouth, emotion, name_emotion="Crying"):
        for (x, y, w, h) in faces:
            # Сглаживаем координаты рамки
            smoothed_x, smoothed_y = self.smooth_values(x + w // 2, y + h // 2 + h // 4)

            # Отображаем лицо
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.circle(frame, (smoothed_x, smoothed_y), 3, (0, 255, 0), -1)

            # Проверяем каждый глаз
            for (eye_center_x, eye_center_y) in eyes:
                # Проверяем, находится ли центр глаза внутри лица
                if x < eye_center_x < x + w and y < eye_center_y < y + h:
                    cv2.circle(frame, (eye_center_x, eye_center_y), 3, (0, 255, 0), -1)

            # Проверяем каждый рот
            for (mouth_center_x, mouth_center_y) in mouth:
                # Проверяем, находится ли центр рта внутри лица
                if x < mouth_center_x < x + w and y < mouth_center_y < y + h:
                    cv2.circle(frame, (mouth_center_x, mouth_center_y), 3, (0, 255, 0), -1)

            # Проверяем наличие эмоции и добавляем текст над лицом
            if emotion:
                cv2.putText(frame, name_emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    def analyze_camera(self):
        # Используем камеру с индексом 0 (обычно это встроенная камера)
        cap = cv2.VideoCapture(0)

        while (cap.isOpened()):
            ret, frame = cap.read()

            # Если камера закрылась, то завершаем работу
            if not ret: break

            faces = self.face_detector.detect_faces(frame)
            eyes = self.face_detector.detect_eyes(frame)
            mouth = self.face_detector.detect_mouth(frame)
            emotion = self.face_detector.detect_crying(frame, faces)

            self.annotate_frame(frame=frame, faces=faces, eyes=eyes, mouth=mouth, emotion=emotion)

            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def analyze_image(self, image, ):
        # Вывод отладочной информации о размере и типе полученного изображения
        # print(f"Received image size: {image.size} bytes")
        # print(f"Received image type: {type(image)}")
        try:
            # Преобразуем изображение в массив байт
            image_bytes = image.read()
            # Преобразуем массив байт в массив numpy
            nparr = np.frombuffer(image_bytes, np.uint8)
            # Декодируем массив numpy в изображение
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Проводим анализ изображения
            faces = self.face_detector.detect_faces(frame)
            eyes = self.face_detector.detect_eyes(frame)
            mouth = self.face_detector.detect_mouth(frame)
            emotion = self.face_detector.detect_crying(frame, faces)

            print(f'Emotion: {emotion}, faces: {len(faces)}, eyes: {len(eyes)}, mouth: {len(mouth)}')

            # Рисуем точки на изображении
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            for (eye_center_x, eye_center_y) in eyes:
                cv2.circle(frame, (eye_center_x, eye_center_y), 3, (0, 255, 0), -1)
            for (mouth_center_x, mouth_center_y) in mouth:
                cv2.circle(frame, (mouth_center_x, mouth_center_y), 3, (0, 255, 0), -1)

            # Покажите изображение с отмеченными точками
            # cv2.namedWindow("Analyzed Image")
            # cv2.resizeWindow("Analyzed Image", 640, 640)
            # cv2.imshow("Analyzed Image", frame)
            # cv2.waitKey(500)
            # cv2.destroyAllWindows()

            # Определим путь к директории сохранения изображения
            # '/home/redalexdad/Документы/GitHub/CryDetectMobile/photo'
            save_path = os.path.join(BASE_DIR, 'photo')
            # Создаем уникальное имя файла
            unique_filename = str(uuid.uuid4()) + '.jpg'
            # Сохраните изображение с отмеченными точками
            cv2.imwrite(os.path.join(save_path, unique_filename), frame)

            return emotion
        except Exception as e:
            print(f"Error during image analysis: {e}")
            return None