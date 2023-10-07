# Generated by Django 4.2.6 on 2023-10-07 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='cover',
            field=models.CharField(choices=[('HARD', 'Hardcover'), ('SOFT', 'Softcover')], default=1, max_length=144),
        ),
    ]
