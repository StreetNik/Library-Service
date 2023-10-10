from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from Library_API.permissions import IsSuperuserOrReadOnly
from .serializers import BorrowingSerializer, BorrowingDetailSerializer
from .models import Borrowing


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    permission_classes = (IsSuperuserOrReadOnly,)
    authentication_classes = (JWTAuthentication,)

    def get_queryset(self):
        queryset = Borrowing.objects.all()
        user = self.request.user

        user_id = self.request.query_params.get("user_id")
        if not user.is_superuser:
            user_id = user.id

        is_active = self.request.query_params.get("is_active")

        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if is_active == "True":
            queryset = queryset.filter(actual_return_date__isnull=False)

        return queryset

    def get_serializer_class(self):
        print(self.action)
        if self.action in ["list", "create"]:
            return BorrowingSerializer

        return BorrowingDetailSerializer

