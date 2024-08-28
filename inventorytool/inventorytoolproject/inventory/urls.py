from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'networks', views.NetworkViewSet)
router.register(r'vpods', views.VPODViewSet)
router.register(r'instances', views.InstanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
