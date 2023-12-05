import datetime

from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from books.models import Book
from .models import Borrowing


class BorrowingAppTests(APITestCase):
    def setUp(self):
        # Create a user
        self.user = get_user_model().objects.create_user(email="testuser@test.com", password="testpassword")

        # Create book
        self.book = Book.objects.create(
            title="testbook",
            author="testauthor",
            inventory=100,
            daily_fee=10.00
        )

        # Create a borrowing with an associated payment
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            expected_return_date=datetime.datetime.now().date() - datetime.timedelta(days=5),
            book=self.book
        )

    def test_borrowing_return_successful(self):
        self.client.force_authenticate(user=self.user)

        # Call the payment_renew endpoint
        url = reverse("borrowings:return-borrowing", kwargs={"pk": self.borrowing.pk})
        response = self.client.post(url)

        # Check that the response has a status code of 200
        expected_redirect_url = reverse(
            "borrowings:borrowing-returned-successfully",
            kwargs={"borrowing_id": self.borrowing.pk}
        )
        self.assertRedirects(response, expected_redirect_url)

        # Check that the payment status is now 'PENDING'
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 101)
