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
        return f'{self.name}'



class Book(models.Model):
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True)
    title = models.CharField(max_length=200)
    publishing_year = models.CharField(max_length=10, null=True)
    number_of_pages = models.CharField(max_length=10)
    # author = models.ForeignKey(Author, on_delete=models.PROTECT, related_name='books')
    authors = models.ManyToManyField(Author, through='BookAuthor', related_name='books')
    image = models.ImageField(upload_to='books/', blank=True, null=True)


    def __str__(self):
        return f'{self.title}, {self.publishing_year}'

class BookAuthor(models.Model):
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    author = models.ForeignKey('Author', on_delete=models.CASCADE)
    added_by_user = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.book.title} - {self.author.name}"