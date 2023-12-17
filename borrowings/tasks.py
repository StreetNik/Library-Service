import datetime

from celery import shared_task
from .models import Borrowing
from telegram_bot.messages import borrowing_overdue_notification


@shared_task
def borrowings_overdue():
    tomorrows_date = datetime.date.today() + datetime.timedelta(days=1)
    queryset = Borrowing.objects.filter(
        actual_return_date__isnull=True, expected_return_date__lte=tomorrows_date
    )

    borrowing_overdue_notification(queryset)
