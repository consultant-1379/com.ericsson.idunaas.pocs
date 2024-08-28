from rest_framework import serializers
from .models import SystemProfile


class SystemProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemProfile
        fields = '__all__'
