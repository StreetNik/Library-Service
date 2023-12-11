from rest_framework import mixins, status
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from telegram_bot.messages import borrowing_creation_notification

from datetime import datetime
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
        book = borrowing.book

        if not request.user.is_superuser and request.user != borrowing.user:
            raise ValidationError(
                "You do not have permission to return this borrowing."
            )

        if borrowing.actual_return_date is not None:
            raise ValidationError("borrowing already inactive")

        borrowing.actual_return_date = datetime.now().date()
        borrowing.save()

        book.inventory += 1
        book.save()

        # Create Fine payment
        fine = None
        if borrowing.actual_return_date > borrowing.expected_return_date:
            fine = create_new_fine_payment(borrowing)

        message = "Borrowing returned successfully!"

        response_data = {
            "message": message,
            "fine_payment_link": None,
            "money_to_pay": None
        }

        if fine:
            message = message + " You have to pay fine during 24 hours!"
            fine_payment_link = fine.session_url
            money_to_pay = fine.money_to_pay
            response_data = {
                "fine_payment_link": fine_payment_link,
                "money_to_pay": money_to_pay,
                "message": message
            }

        serializer = BorrowingReturnSerializer(data=response_data)
        serializer.is_valid(raise_exception=True)
        response_data = serializer.data

        return Response(response_data, status=status.HTTP_200_OK)
