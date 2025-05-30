# Generated by Django 5.1.7 on 2025-04-21 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0023_borrow_returned_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='date_of_birth',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='book',
            name='publishing_year',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
