from django.db import models
from borrowings.models import Borrowing


PAYMENT_STATUS_CHOICES = (("PENDING", "Pending"), ("PAID", "Paid"))

PAYMENT_TYPE_CHOICES = (("PAYMENT", "Payment"), ("FINE", "Fine"))


class Payment(models.Model):
    status = models.CharField(choices=PAYMENT_STATUS_CHOICES, default=1, max_length=144)
    type = models.CharField(choices=PAYMENT_TYPE_CHOICES, default=1, max_length=144)
    borrowing = models.ForeignKey(Borrowing, on_delete=models.CASCADE)
    session_url = models.URLField()
    session_id = models.CharField(max_length=240)
    money_to_pay = models.DecimalField(max_digits=4, decimal_places=2)
