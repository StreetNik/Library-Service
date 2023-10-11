import requests
import os
from dotenv import load_dotenv

from borrowings.models import Borrowing


load_dotenv()
message_url = str(os.getenv("MESSAGE_URL"))


def borrowing_creation(borrowing: Borrowing) -> None:
    message = f"New Borrowing Created \n" \
              f"Borrowing: {borrowing.pk} \n" \
              f"User: {borrowing.user_id}, {borrowing.user.first_name} {borrowing.user.last_name} \n" \
              f"Book: {borrowing.book.title} \n" \
              f"Daily fee: {borrowing.book.daily_fee}$ \n" \
              f"Dates: {borrowing.borrow_date} - {borrowing.expected_return_date}, " \

    requests.get(message_url.format(message))
