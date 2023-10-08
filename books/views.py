from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from Library_API.permissions import IsSuperuserOrReadOnly
from .serializers import BookSerializer
from .models import Book


class BookViewSet(ModelViewSet):
    permission_classes = (IsSuperuserOrReadOnly,)
    authentication_classes = (JWTAuthentication,)
    serializer_class = BookSerializer
    queryset = Book.objects.all()
