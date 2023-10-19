import stripe
from decimal import *
from django.conf import settings

from borrowings.models import Borrowing
from .models import Payment


stripe.api_key = settings.STRIPE_SECRET_KEY


def create_new_checkout_session(borrowing:Borrowing, price: Decimal) -> stripe.checkout.Session:
    checkout_session = stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": int(price * 100),
                    "product_data": {
                        "name": borrowing.book.title
                    },
                },
                'quantity': 1,
            },
        ],
        mode='payment',
        success_url='http://127.0.0.1:8000/api/payments/',
        cancel_url='http://127.0.0.1:8000/api/payments/',
    )

    return checkout_session


def create_new_payment(borrowing: Borrowing) -> Payment:
    expected_days_rented = (borrowing.expected_return_date - borrowing.borrow_date).days
    price = expected_days_rented * borrowing.book.daily_fee

    session = create_new_checkout_session(borrowing, price)
    payment = Payment.objects.create(
        borrowing=borrowing,
        session_id=session.id,
        session_url=session.url,
        money_to_pay=price
    )

    return payment
