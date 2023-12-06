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

    def get_queryset(self):
        queryset = self.queryset

        title = self.request.query_params.get("title")
        author = self.request.query_params.get("author")

        if title:
            queryset = queryset.filter(title__icontains=title)
        if author:
            queryset = queryset.filter(author__icontains=author)

        return queryset
