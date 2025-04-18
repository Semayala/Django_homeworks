# Generated by Django 5.1.7 on 2025-04-04 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isbn', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('title', models.CharField(max_length=200)),
                ('publishing_year', models.CharField(max_length=10)),
                ('number_of_pages', models.CharField(max_length=10)),
            ],
        ),
        migrations.DeleteModel(
            name='Library',
        ),
    ]
