from django.urls import path
from .views import ActorListView, ActorDetailView, ActorDetailsListView, ActorDetailsDetailView

urlpatterns = [
    path('actors/', ActorListView.as_view(), name='actor-list'),
    path('actors/<int:pk>/', ActorDetailView.as_view(), name='actor-detail'),
    path('actor-details/', ActorDetailsListView.as_view(), name='actor-details-list'),
    path('actor-details/<int:pk>/', ActorDetailsDetailView.as_view(), name='actor-details-detail'),
]
