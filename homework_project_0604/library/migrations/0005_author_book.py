# Generated by Django 5.1.7 on 2025-04-04 19:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0004_rename_date_of_place_author_place_of_birth'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='book',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='books', to='library.book'),
        ),
    ]
