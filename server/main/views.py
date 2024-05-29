import io
import base64
from PIL import Image

from django.core.files.base import ContentFile
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from main.FaceDetector.FaceDetector import CameraAnalyzer




@api_view(['GET'])
def analyze_camera(request):
    # print('request.method: ', request.method)
    # analyzer = CameraAnalyzer()
    # analyzer.analyze_camera()  # Вызываем метод анализа камеры
    return Response({"message": "Анализ камеры завершен"})

@api_view(['POST'])
def analyze_camera_photo(request):
    print('CAMERA ANALYZE PHOTO')
    if request.method == 'POST' and request.FILES['photo']:
        photo = request.FILES['photo']
        print(f'photo is {photo}, size is {photo.size}')

        # Проводим анализ изображения с помощью вашего класса CameraAnalyzer
        analyzer = CameraAnalyzer()
        try:
            result = analyzer.analyze_image(photo)
            if result is not None:
                # Возвращаем результат анализа в формате JSON
                return JsonResponse({'emotion_detected': result})
            else:
                # Если результат анализа пустой, возвращаем сообщение об ошибке
                return JsonResponse({'error': 'Failed to detect emotion'}, status=500)
        except Exception as e:
            print(f"Error during image analysis: {e}")
            return JsonResponse({'error': 'An error occurred during image analysis'}, status=500)
    else:
        return JsonResponse({'error': 'Please provide image'}, status=400)

# Создаем экземпляр класса CameraAnalyzer
analyzer = CameraAnalyzer()

# Представление для анализа видеопотока в реальном времени
@api_view(['GET'])
def analyze_camera_stream(request):
    # Запускаем анализ видеопотока в реальном времени
    analyzer.analyze_camera()
    return JsonResponse({'status': 'success'})


@api_view(['GET'])
def test_api_get(request):
    # Просто возвращаем JSON-ответ
    return JsonResponse({'message': 'Привет от Django!'})


@api_view(['POST'])
def test_api_post(request):
    data = request.data
    print('data', data)
    # Просто возвращаем JSON-ответ
    return JsonResponse({'message': data})
