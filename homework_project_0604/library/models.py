from django.db import models

# Create your models here.

class Author(models.Model):
    name = models.CharField(max_length=20)
    date_of_birth = models.CharField(max_length=20)
    place_of_birth = models.CharField(max_length=20)
    nationality = models.CharField(max_length=20)
    date_of_death = models.CharField(max_length=20, blank=True, null=True)
    place_of_death = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f'{self.name}, {self.date_of_birth}'



class Book(models.Model):
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True)
    title = models.CharField(max_length=200)
    publishing_year = models.CharField(max_length=10, null=True)
    number_of_pages = models.CharField(max_length=10)
    author = models.ForeignKey(Author, related_name='books', on_delete=models.CASCADE)


    def __str__(self):
        return f'{self.title}, {self.publishing_year}'