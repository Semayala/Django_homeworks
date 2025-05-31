from django.db import models
from django.contrib.auth.models import User
from django.db import IntegrityError


# Create your models here.


class Author(models.Model):
    name = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    place_of_birth = models.CharField(max_length=20)
    nationality = models.CharField(max_length=20)
    date_of_death = models.DateField(max_length=20, blank=True, null=True)
    place_of_death = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f'{self.name}'



class Book(models.Model):
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True)
    title = models.CharField(max_length=200)
    publishing_year = models.IntegerField(blank=True, null=True)
    number_of_pages = models.CharField(max_length=10)
    authors = models.ManyToManyField(Author, through='BookAuthor', related_name='books')
    image = models.ImageField(upload_to='books/', blank=True, null=True)
    available_copies = models.IntegerField(default=0)
    is_borrowed = models.BooleanField(default=False)



    def __str__(self):
        return f'{self.title}, {self.publishing_year}'


    def calculated_available_copies(self):
        total_borrows = Borrow.objects.filter(book=self).count()
        return max(0, self.available_copies - total_borrows)

    def borrow(self, user):
        if self.available_copies > 0:
            try:
                Borrow.objects.create(user=user, book=self)
                self.available_copies -= 1
                self.save()
                return True
            except IntegrityError:
                return False  # Already borrowed
        return False  # Not available

    def return_copy(self, user):
        borrow = Borrow.objects.filter(user=user, book=self).first()
        if borrow:
            borrow.delete()
            self.available_copies += 1
            self.save()
            return True
        return False


class Borrow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrowed_at = models.DateTimeField(auto_now_add=True)
    returned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-borrowed_at']

    def __str__(self):
        return f"{self.user.username} → {self.book.title} ({self.borrowed_at.strftime('%Y-%m-%d %H:%M')})"


class BookAuthor(models.Model):
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    author = models.ForeignKey('Author', on_delete=models.CASCADE)
    added_by_user = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.book.title} - {self.author.name}"