from rest_framework import generics
from .models import Actor, ActorDetails
from .serializers import ActorSerializer, ActorDetailsSerializer

class ActorListView(generics.ListCreateAPIView):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer

class ActorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer

class ActorDetailsListView(generics.ListCreateAPIView):
    queryset = ActorDetails.objects.all()
    serializer_class = ActorDetailsSerializer

class ActorDetailsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ActorDetails.objects.all()
    serializer_class = ActorDetailsSerializer