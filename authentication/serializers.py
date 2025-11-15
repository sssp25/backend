from django.contrib.auth.models import User
from rest_framework import serializers

ALLOWED_EMAIL_DOMAIN = 'sunrint.hs.kr'

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id', 'username')

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        
        if not value.lower().endswith('@' + ALLOWED_EMAIL_DOMAIN):
            raise serializers.ValidationError(
                f"Only @{ALLOWED_EMAIL_DOMAIN} email addresses are allowed"
            )
        
        return value
