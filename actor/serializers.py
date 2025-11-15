from rest_framework import serializers
from .models import Actor, ActorDetails

class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = '__all__'

class ActorDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActorDetails
        fields = '__all__'
