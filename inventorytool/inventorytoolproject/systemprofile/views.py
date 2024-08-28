from rest_framework import viewsets
from .models import SystemProfile
from .serializers import SystemProfileSerializer


class SystemProfileViewSet(viewsets.ModelViewSet):
    queryset = SystemProfile.objects.all()
    serializer_class = SystemProfileSerializer
