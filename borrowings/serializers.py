from rest_framework import serializers

from .models import Borrowing
from books.serializers import BookSerializer


class BorrowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = [
            "id", "borrow_date", "expected_return_date",
            "actual_return_date", "book", "user"
        ]


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookSerializer()
