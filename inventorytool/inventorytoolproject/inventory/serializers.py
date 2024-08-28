from rest_framework import serializers
from .models import Network, VPOD, Instance


class InstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instance
        fields = '__all__'


class VPODSerializer(serializers.ModelSerializer):
    Instances = InstanceSerializer(many=True)

    class Meta:
        model = VPOD
        fields = '__all__'


class NetworkSerializer(serializers.ModelSerializer):
    VPODS = VPODSerializer(many=True)

    class Meta:
        model = Network
        fields = '__all__'
