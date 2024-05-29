# face_analyzer/urls.py
from django.urls import path
from main.views import analyze_camera, analyze_camera_photo, analyze_camera_stream, test_api_get, test_api_post

urlpatterns = [
    path('analyze_camera/', analyze_camera, name='analyze_camera'),
    path('analyze_camera_photo/', analyze_camera_photo, name='analyze_camera_photo'),
    path('analyze_camera_stream/', analyze_camera_stream, name='analyze_camera_stream'),
    path('test_api_get/', test_api_get, name='test_api_get'),
    path('test_api_post/', test_api_post, name='test_api_post'),
]
