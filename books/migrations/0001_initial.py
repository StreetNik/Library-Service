# Generated by Django 4.2.6 on 2023-10-07 18:07

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Book",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=144)),
                ("author", models.CharField(max_length=144)),
                (
                    "cover",
                    models.IntegerField(
                        choices=[("HARD", "Hardcover"), ("SOFT", "Softcover")],
                        default=1,
                    ),
                ),
                ("inventory", models.PositiveIntegerField()),
                ("daily_fee", models.DecimalField(decimal_places=2, max_digits=5)),
            ],
        ),
    ]
