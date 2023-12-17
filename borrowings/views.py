from rest_framework import mixins, status
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from telegram_bot.messages import borrowing_creation_notification

from .serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer,
    CreateBorrowingSerializer,
    AdminCreateBorrowingSerializer, BorrowingReturnSerializer,
)
from .models import Borrowing
from payments.utils import create_new_payment, create_new_fine_payment


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        pk = response.data.get("id")
        borrowing = Borrowing.objects.get(id=pk)

        borrowing_creation_notification(borrowing)
        create_new_payment(borrowing)

        return response

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
        if self.action == "list":
            return BorrowingSerializer
        if self.action == "create":
            if self.request.user.is_superuser:
                return AdminCreateBorrowingSerializer
            return CreateBorrowingSerializer

        return BorrowingDetailSerializer

    @action(detail=True, methods=["POST"], url_path="return", url_name="return-borrowing")
    def return_borrowing(self, request, pk):
        """Endpoint to handle the return of a borrowed books."""
        borrowing = get_object_or_404(Borrowing, pk=pk)

        serializer = BorrowingReturnSerializer(
            instance=borrowing,
            data={},
            context={
                "user": self.request.user
            },
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.update(borrowing, {})
        response_data = serializer.data

        return Response(response_data, status=status.HTTP_200_OK)
