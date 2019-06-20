from django.db import models
import datetime
from django.utils import timezone


class Author(models.Model):
    author_name = models.CharField(max_length=200)
    birthday = models.DateField()
    nationality = models.CharField(max_length=200)

    def __str__(self):
        return self.author_name


class Genre(models.Model):
    genre_name = models.CharField(max_length=200)

    def __str__(self):
        return self.genre_name

# Create your models here.


class Book(models.Model):
    book_title = models.CharField(max_length=200)
    pub_date = models.DateField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    def __str__(self):
        return self.book_title

