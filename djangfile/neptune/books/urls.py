from django.urls import path
from . import views

app_name = "books"
urlpatterns = [
    path("", views.index, name="index"),
    path("<int:author_id>/", views.author, name="author"),
    path("<int:author_id>/<int:book_id>", views.book, name="book"),
    path("genre/<int:genre_id>", views.genre, name="genre")
]