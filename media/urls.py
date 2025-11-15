from django.urls import path

from .views import get_trending_videos, search_media, upload_media, upload_video, VideoView, PhotoView

urlpatterns = [
    path('trending', get_trending_videos),
    path('search/<str:mtype>', search_media),
    path('upload', upload_media),
    path('upload/video', upload_video),
    path('upload/image', upload_media),
    path('video/<str:vid>', VideoView.as_view()),
    path('photo/<str:iid>', PhotoView.as_view())
]
