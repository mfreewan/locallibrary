import datetime
import uuid
from django.db import models
from django.forms import ModelForm
from django.urls import reverse  # used to generate URLs by reversing the URL patterns
from django.contrib.auth.models import User  # required to assign user in borrower
from django.contrib.auth.models import User
from datetime import date

from nbformat import ValidationError
from django.utils.translation import gettext_lazy as _

# Create your models here.

## create a model for the genre will contain name field


class Genre(models.Model):
    name = models.CharField(
        max_length=200, help_text="Enter a Book genre (e.g. Science Fiction)"
    )

    def __str__(self):
        """String for rapresenting the mode object"""
        return self.name


## Create a model for language will contain name field


class Language(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100, null=True)  # Allow null values

    def __str__(self):
        """String for rapresenting the mode object"""
        return self.name


## create a model for the book will contain title , author , summary ,isbn , genre , language


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey("Author", on_delete=models.SET_NULL, null=True)
    summary = models.TextField(
        max_length=1000, help_text="Enter a breif discribtion for the book "
    )
    isbn = models.CharField(
        "ISBN",
        max_length=13,
        help_text='13 Character <a href="https://www.isbn-international.org/content"',
    )
    genre = models.ManyToManyField(Genre, help_text="Select a genre for this book ")
    language = models.ForeignKey("Language", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        """string for representing the model object"""
        return self.title

    def get_absolute_url(self):
        """returns the url to access a detail record for this book"""
        return reverse("book-detail", args=[str(self.id)])

    ##

    def display_genre(self):
        """Create a string for the Genre. This is required to display genre in Admin."""
        return ", ".join(genre.name for genre in self.genre.all()[:3])

    display_genre.short_description = "Genre"


## create  a model for book instance will contain book , imprint , due back , id , status , borrower
class BookInstance(models.Model):
    """Model representing a specific copy of a book (i.e. that can be borrowed from the library)."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        help_text="Unique ID for this particular book across whole library",
    )
    book = models.ForeignKey("Book", on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    LOAN_STATUS = (
        ("m", "Maintenance"),
        ("o", "On loan"),
        ("a", "Available"),
        ("r", "Reserved"),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default="m",
        help_text="Book availability",
    )

    class Meta:
        ordering = ["due_back"]

    def __str__(self):
        """String for representing the Model object."""
        return f"{self.id} ({self.book.title})"

    @property
    def is_overdue(self):
        """Determines if the book is overdue based on due date and current date."""
        return bool(self.due_back and date.today() > self.due_back)


##Create a model for author will conain name , Date of birth , Date of Death , books


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField("Died", null=True, blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def get_absolute_url(self):
        """Returns the url to access a particular author instance"""
        return reverse("author-detail", args=[str(self.id)])

    def __str__(self):
        """string for representing the model object"""
        return f"{self.last_name} {self.first_name}"


class RenewBookModelForm(ModelForm):
    def clean_due_back(self):
        data = self.cleaned_data["due_back"]

        # Check if a date is not in the past.
        if data < datetime.date.today():
            raise ValidationError(("Invalid date - renewal in past"))

        # Check if a date is in the allowed range (+4 weeks from today).
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(("Invalid date - renewal more than 4 weeks ahead"))

        # Remember to always return the cleaned data.
        return data

    class Meta:
        model = BookInstance
        fields = ["due_back"]
        labels = {"due_back": _("New renewal date")}
        help_texts = {
            "due_back": _("Enter a date between now and 4 weeks (default 3).")
        }
