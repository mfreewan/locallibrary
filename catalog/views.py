from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from audioop import reverse
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views import generic

from django.contrib import admin
from django.contrib.auth.mixins import LoginRequiredMixin

from catalog.forms import RenewBookForm

from .models import Author, Book, BookInstance, Genre

from django.urls import reverse, reverse_lazy
from catalog.forms import RenewBookForm
from django.views.generic.edit import CreateView, DeleteView, UpdateView

# Create your views here.


def index(request):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact="a").count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    context = {
        "num_books": num_books,
        "num_instances": num_instances,
        "num_instances_available": num_instances_available,
        "num_authors": num_authors,
        "num_visits": num_visits,
    }

    return render(request, "index.html", context=context)


# create view for book list


class BookListView(generic.ListView):
    model = Book
    book_list = "book_list"  # your own name for the list as a template variable
    template_name = "main/book_list.html"  # Specify your own template name/location

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(BookListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context["some_data"] = "This is just some data"
        return context


class BookDetailView(generic.DetailView):
    model = Book
    template_name = "catalog/book_detail.html"

    def book_detail_view(request, primary_key):
        try:
            book = Book.objects.get(pk=primary_key)
        except Book.DoesNotExist:
            raise Http404("Book does not exist")

        return render(request, context={"book": book})


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""

    model = BookInstance
    template_name = "catalog/bookinstance_list_borrowed_user.html"
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact="o")
            .order_by("due_back")
        )


def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == "POST":
        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data["renewal_date"]
            book_instance.save()

            # redirect to a new URL:
            # return HttpResponseRedirect(reverse('all-borrowed'))
            return HttpResponse("renewed successfully")

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={"renewal_date": proposed_renewal_date})

    context = {
        "form": form,
        "book_instance": book_instance,
    }

    return render(request, "catalog/book_renew_librarian.html", context)


class Borrow(generic.ListView):
    model = BookInstance
    borrow = "borrow"  # your own name for the list as a template variable
    # Specify your own template name/location
    template_name = "catalog/borrowed_view.html"

    @staff_member_required
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(Borrow, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context["some_data"] = "This is just some data"
        return context


class AuthorListView(generic.ListView):
    model = Author
    author_list = "author_list"  # your own name for the list as a template variable
    template_name = "catalog/author_list.html"  # The HTML template for this view

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(AuthorListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context["some_data"] = "This is just some data"
        return context


class AuthorDetailView(generic.DetailView):
    model = Author
    template_name = "catalog/author_detail.html"  # The HTML template for this view

    def author_detail_view(request, primary_key):
        try:
            author = Author.objects.get(pk=primary_key)
        except Author.DoesNotExist:
            raise Http404("Author does not exist")

        # The name of the variable to access the author in the template
        return render(request, context={"author": author})


class AuthorCreate(CreateView):
    model = Author
    fields = ["first_name", "last_name", "date_of_birth", "date_of_death"]
    initial = {"date_of_death": "11/06/2020"}


class AuthorUpdate(UpdateView):
    model = Author
    # Not recommended (potential security issue if more fields added)
    fields = "__all__"


class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy("author-list")


class BookCreate(CreateView):
    model = Book
    fields = ["title", "author", "summary", "isbn"]
    initial = {"genre": "language"}


class BookUpdate(UpdateView):
    model = Book
    # Not recommended (potential security issue if more fields added)
    fields = "__all__"


class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy("books")
