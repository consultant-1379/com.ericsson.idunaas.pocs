from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'system_profiles', views.SystemProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

