import stripe
from Library_API import settings
from datetime import datetime
from celery import shared_task

from .models import Payment


stripe.api_key = settings.STRIPE_SECRET_KEY

@shared_task
def update_expired_payments_status():
    queryset = Payment.objects.filter(status="PENDING")

    for payment in queryset:
        session_id = payment.session_id
        session = stripe.checkout.Session.retrieve(session_id)

        expiration_time_str = session.metadata['expiration_time']
        expiration_time = datetime.utcfromtimestamp(int(expiration_time_str))
        current_time = datetime.utcnow()

        if current_time > expiration_time:
            payment.status = "EXPIRED"
            payment.save()
