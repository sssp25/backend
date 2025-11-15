from rest_framework import serializers
from .models import Media, OneWeekVideoStatics

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        exclude = ('is_video',)
        read_only_fields = ('id', 'actor', 'uploaded_at', 'is_video')

class OneWeekVideoStaticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OneWeekVideoStatics
        fields = '__all__'