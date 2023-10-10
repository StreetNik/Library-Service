from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from datetime import datetime
from .serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer,
    CreateBorrowingSerializer,
    AdminCreateBorrowingSerializer,
    ReturnBorrowingSerializer
)
from .models import Borrowing


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    permission_classes = (IsAuthenticated,)
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
        if self.action == "list":
            return BorrowingSerializer
        if self.action == "create":
            if self.request.user.is_superuser:
                return AdminCreateBorrowingSerializer
            return CreateBorrowingSerializer

        return BorrowingDetailSerializer

    @action(detail=False, methods=["POST"])
    def return_borrowing(self, request, pk):
        serializer_class = ReturnBorrowingSerializer
        serializer = serializer_class(data=request.data)

        if serializer.is_valid():
            borrowing = Borrowing.objects.get(id=pk)
            book = borrowing.book

            if borrowing.actual_return_date is not None:
                raise ValidationError("borrowing already inactive")

            borrowing.actual_return_date = datetime.now()
            borrowing.save()

            book.inventory += 1
            book.save()

            return Response({"message": "Borrowing returned successfully"})

        return Response(serializer.errors, status=400)
