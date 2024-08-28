from rest_framework import viewsets
from .models import Network, VPOD, Instance
from .serializers import NetworkSerializer, VPODSerializer, InstanceSerializer


class NetworkViewSet(viewsets.ModelViewSet):
    queryset = Network.objects.all()
    serializer_class = NetworkSerializer


class VPODViewSet(viewsets.ModelViewSet):
    queryset = VPOD.objects.all()
    serializer_class = VPODSerializer


class InstanceViewSet(viewsets.ModelViewSet):
    queryset = Instance.objects.all()
    serializer_class = InstanceSerializer
