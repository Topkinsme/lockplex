from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('lockplex/', lockplex, name='lockplex'),
    path('start/', start, name='start'),
    path('upload-audio/', upload_audio, name='upload_audio'),
    path('recordings/', recordings_list, name='recordings_list'),
]