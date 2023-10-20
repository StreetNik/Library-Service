from rest_framework import serializers
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
            "actual_return_date",
            "book",
            "user",
        ]
        read_only_fields = ["user"]

    def validate(self, attrs):
        book = attrs.get("book")
        if book.inventory < 1:
            raise serializers.ValidationError("Book are not available!")

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
