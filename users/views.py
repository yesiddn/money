from rest_framework import permissions
from rest_framework import generics
from users.serializers import UserSerializer
from django.contrib.auth import get_user_model

class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [
        permissions.AllowAny,
    ]