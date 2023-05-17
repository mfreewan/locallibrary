from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import BookInstance


class BorrowViewTestCase(TestCase):
    def setUp(self):
        # Create a user with staff permissions
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.user.is_staff = True
        self.user.save()

        # Create some book instances
        self.book1 = BookInstance.objects.create(book="Book 1", imprint="Imprint 1")
        self.book2 = BookInstance.objects.create(book="Book 2", imprint="Imprint 2")

    def test_borrow_view_with_login(self):
        # Log in as the test user
        self.client.login(username="testuser", password="12345")

        # Make a GET request to the view
        response = self.client.get(reverse("borrow"))

        # Check that the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Check that the correct template was used
        self.assertTemplateUsed(response, "catalog/borrowed_view.html")

        # Check that the context contains the expected data
        self.assertEqual(response.context["some_data"], "This is just some data")

        # Check that the context contains the expected book instances
        self.assertQuerysetEqual(
            response.context["bookinstance_list"],
            [repr(self.book1), repr(self.book2)],
            ordered=False,
        )

    def test_borrow_view_without_login(self):
        # Log out the client
        self.client.logout()

        # Make a GET request to the view
        response = self.client.get(reverse("borrow"))

        # Check that the response status code is 302 (redirect to login)
        self.assertEqual(response.status_code, 302)

        # Check that the client was redirected to the login page
        self.assertRedirects(response, "/accounts/login/?next=/catalog/borrow/")
