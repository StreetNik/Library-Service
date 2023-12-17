import datetime
from freezegun import freeze_time
from decimal import Decimal

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from books.models import Book
from .models import Payment, Borrowing
from .tasks import update_expired_payments_status
from .utils import create_new_checkout_session, create_new_payment, create_new_fine_payment


class PaymentAppTests(APITestCase):
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
            expected_return_date=datetime.datetime.now().date() + datetime.timedelta(days=5),
            book=self.book
        )

        # Create session
        self.session = create_new_checkout_session(self.borrowing, Decimal(100))

        # Create payment
        self.payment = Payment.objects.create(
            status="EXPIRED",
            borrowing=self.borrowing,
            session_id=self.session.id,
            session_url=self.session.url,
            money_to_pay=10.00
        )

    def test_payment_renew_successful(self):
        # Authenticate the user (if needed)
        self.client.force_authenticate(user=self.user)

        # Call the payment_renew endpoint
        url = reverse("payments:payment_renew", kwargs={"pk": self.payment.pk})
        response = self.client.post(url)

        # Check that the response has a status code of 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the payment status is now 'PENDING'
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, "PENDING")

    def test_payment_renew_not_expired(self):
        # Authenticate the user (if needed)
        self.client.force_authenticate(user=self.user)

        # Change payment status to 'PAID' to simulate a non-expired payment
        self.payment.status = "PAID"
        self.payment.save()

        # Call the payment_renew endpoint
        url = reverse("payments:payment_renew", kwargs={"pk": self.payment.pk})
        response = self.client.post(url)

        # Check that the response has a status code of 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @freeze_time(datetime.datetime.now())
    def test_update_expired_payments_status(self):
        self.payment.status = "PENDING"
        self.payment.save()

        update_expired_payments_status()

        self.assertEqual(self.payment.status, "PENDING")

        with freeze_time(datetime.datetime.now() + datetime.timedelta(days=1, hours=1)):
            update_expired_payments_status()

        self.payment.refresh_from_db()

        self.assertEqual(self.payment.status, "EXPIRED")

    def test_create_new_payment(self):
        money_to_pay = 50
        new_payment = create_new_payment(self.borrowing)

        self.assertEqual(new_payment.money_to_pay, money_to_pay)
        self.assertEqual(new_payment.type, self.payment.type)

    def test_create_new_fine(self):
        money_to_pay = 100
        self.borrowing.actual_return_date = datetime.datetime.now().date() + datetime.timedelta(days=10)
        self.borrowing.save()
        new_fine = create_new_fine_payment(self.borrowing)

        self.assertEqual(new_fine.money_to_pay, money_to_pay)
        self.assertEqual(new_fine.type, "FINE")
