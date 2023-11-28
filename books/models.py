from django.db import models


COVER_CHOICES = (("HARD", "Hardcover"), ("SOFT", "Softcover"))


class Book(models.Model):
    title = models.CharField(max_length=144)
    author = models.CharField(max_length=144)
    cover = models.CharField(choices=COVER_CHOICES, default=1, max_length=144)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.title} {self.author} - {self.daily_fee}$/day"
