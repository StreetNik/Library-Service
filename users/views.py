from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import UserSerializer, TokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer
