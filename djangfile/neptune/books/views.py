from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
from .models import Book, Author

def index(request):
    random_books = Book.objects.all()[:5]
    context = {"random_books": random_books}
    return render(request, "books/index.html", context)

def book(request, author_id, book_id):
    book = Book.objects.get(pk=book_id)
    context = {"book":book}
    return render(request, "books/book.html", context)

def author(request, author_id):
    author = Author.objects.get(pk=author_id)
    author_books = Book.objects.filter(author=author)
    context = {"author":author, "author_books":author_books}
    return render(request, "books/author.html", context)

def genre(request, genre_id):
    return HttpResponse("Genre")