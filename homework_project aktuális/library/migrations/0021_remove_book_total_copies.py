# Generated by Django 5.1.7 on 2025-04-19 19:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0020_remove_book_is_borrowed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='total_copies',
        ),
    ]
