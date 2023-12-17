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


class OrderSuccessSerializer(serializers.Serializer):
    customer_email = serializers.EmailField()
    amount = serializers.DecimalField(max_digits=5, decimal_places=2)
    payment_status = serializers.CharField(max_length=20)


class OrderCancelSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=5, decimal_places=2)
    payment_status = serializers.CharField(max_length=20)
    payment_url = serializers.URLField()
    pay_until = serializers.CharField(default="You can pay only during 24 hours after borrowing!!!")
