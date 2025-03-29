from django.db import models

# Create your models here.

class Library(models.Model):
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    publishing_year = models.CharField(max_length=10)
    number_of_pages = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.author}: {self.title}'
