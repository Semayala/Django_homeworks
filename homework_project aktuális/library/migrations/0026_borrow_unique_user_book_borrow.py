# Generated by Django 5.1.7 on 2025-04-27 09:07

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0025_alter_borrow_options_alter_borrow_unique_together'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='borrow',
            constraint=models.UniqueConstraint(fields=('user', 'book'), name='unique_user_book_borrow'),
        ),
    ]
