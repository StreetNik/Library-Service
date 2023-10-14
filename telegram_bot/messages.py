import requests
import os
from dotenv import load_dotenv

from borrowings.models import Borrowing


load_dotenv()
message_url = str(os.getenv("MESSAGE_URL"))


def borrowing_creation_notification(borrowing: Borrowing) -> None:
    message = f"New Borrowing Created \n" \
              f"Borrowing: {borrowing.pk} \n" \
              f"User: {borrowing.user_id}, {borrowing.user.first_name} {borrowing.user.last_name} \n" \
              f"Book: {borrowing.book.title} \n" \
              f"Daily fee: {borrowing.book.daily_fee}$ \n" \
              f"Expected return period: {borrowing.borrow_date} - {borrowing.expected_return_date}"

    requests.get(message_url.format(message))


def borrowing_overdue_notification(borrowings_queryset):
    message = f"Overdue Alert \n \n"

    if not borrowings_queryset:
        message += f"No borrowings overdue today!"
    else:
        for borrowing in borrowings_queryset:
            message += f"Borrowing: {borrowing.pk} \n" \
                f"User: {borrowing.user_id}, {borrowing.user.first_name} {borrowing.user.last_name} \n" \
                f"Book: {borrowing.book.title} \n" \
                f"Expected return period: {borrowing.borrow_date} - {borrowing.expected_return_date} \n \n"

    requests.get(message_url.format(message))
