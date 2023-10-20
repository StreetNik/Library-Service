from rest_framework import serializers

from .models import Payment
from users.serializers import UserProfileSerializer
from books.serializers import BookSerializer


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = [
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay"
        ]


class PaymentDetailSerializer(PaymentSerializer):
    user = UserProfileSerializer(source="borrowing.user")
    book = BookSerializer(source="borrowing.book")

    class Meta:
        model = Payment
        fields = [
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay",
            "book",
            "user",
        ]
