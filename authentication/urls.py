from django.urls import path
from .views import google_login, logout

urlpatterns = [
    path('google/', google_login, name='google-login'),
    path('logout/', logout, name='logout'),
]
