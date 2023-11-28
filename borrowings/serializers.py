from rest_framework import serializers
from django.contrib.auth import get_user

from payments.models import Payment
from .models import Borrowing
from books.serializers import BookSerializer
from payments.serializers import PaymentSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True)

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "payments",
            "book",
            "user",
        ]


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookSerializer()


class CreateBorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
            "user",
        ]
        read_only_fields = ["user"]

    def validate(self, attrs):
        book = attrs.get("book")
        user = self.context["request"].user
        if book.inventory < 1:
            raise serializers.ValidationError("Book are not available!")

        user_unpaid_payments = Payment.objects.filter(borrowing__user=user).exclude(status="PAID").count()

        if user_unpaid_payments != 0:
            raise serializers.ValidationError("You have to pay for all borrowings before make a new one!")

        return attrs

    def create(self, validated_data):
        book = validated_data.pop("book")
        book.inventory -= 1
        book.save()

        borrowing = Borrowing.objects.create(
            book=book, **validated_data, user=self.context["request"].user
        )

        return borrowing


class AdminCreateBorrowingSerializer(CreateBorrowingSerializer):
    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        ]

    def create(self, validated_data):
        book = validated_data.pop("book")
        book.inventory -= 1
        book.save()

        borrowing = Borrowing.objects.create(book=book, **validated_data)

        return borrowing


class BorrowingReturnSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=255)
    fine_payment_link = serializers.URLField(allow_null=True)
    money_to_pay = serializers.DecimalField(max_digits=8, decimal_places=2, allow_null=True)
