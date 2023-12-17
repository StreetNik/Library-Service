from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied

from payments.models import Payment
from payments.utils import create_new_fine_payment
from .models import Borrowing
from books.serializers import BookSerializer
from payments.serializers import PaymentSerializer

from datetime import datetime


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

        user_unpaid_payments = (
            Payment.objects.filter(borrowing__user=user).exclude(status="PAID").count()
        )

        if user_unpaid_payments != 0:
            raise serializers.ValidationError(
                "You have to pay for all borrowings before make a new one!"
            )

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
            "book",
            "user",
        ]

    def create(self, validated_data):
        book = validated_data.pop("book")
        book.inventory -= 1
        book.save()

        borrowing = Borrowing.objects.create(book=book, **validated_data)

        return borrowing


class BorrowingReturnSerializer(serializers.ModelSerializer):
    message = serializers.CharField(
        max_length=255, default="Borrowing returned successfully!"
    )
    fine_payment_link = serializers.URLField(allow_null=True, default=None)
    money_to_pay = serializers.DecimalField(
        max_digits=8, decimal_places=2, allow_null=True, default=None
    )

    class Meta:
        model = Borrowing
        fields = ("id", "message", "fine_payment_link", "money_to_pay")
        read_only_fields = ("message", "fine_payment_link", "money_to_pay")

    def validate(self, attrs):
        user = self.context.get("user")
        borrowing = self.instance
        if not user.is_superuser and user != borrowing.user:
            raise PermissionDenied(
                "You do not have permission to return this borrowing."
            )

        if borrowing.actual_return_date is not None:
            raise ValidationError("Borrowing already inactive")

        return super().validate(attrs)

    def update(self, instance, validated_data):
        # Update return date
        borrowing = instance
        borrowing.actual_return_date = datetime.now().date()
        borrowing.save()

        # Update book inventory
        book = borrowing.book
        book.inventory += 1
        book.save()

        # Create fine payment
        if borrowing.actual_return_date > borrowing.expected_return_date:
            fine = create_new_fine_payment(borrowing)

            validated_data["fine_payment_link"] = (fine.session_url,)
            validated_data["money_to_pay"] = (fine.money_to_pay,)
            validated_data[
                "message"
            ] = "Borrowing returned successfully! You have to pay fine during 24 hours!"

        return borrowing

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Include virtual fields in the representation
        representation["message"] = (
            self.validated_data.get("message") or self.fields["message"].default
        )
        representation["money_to_pay"] = (
            self.validated_data.get("money_to_pay")
            or self.fields["money_to_pay"].default
        )
        representation["fine_payment_link"] = (
            self.validated_data.get("fine_payment_link")
            or self.fields["money_to_pay"].default
        )

        return representation
