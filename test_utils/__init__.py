"""
Test utilities.

Since pytest discourages putting __init__.py into testdirectory
(i.e. making tests a package) one cannot import from anywhere
under tests folder. However, some utility classes/methods might be useful
in multiple test modules (i.e. factoryboy factories, base test classes).

So this package is the place to put them.
"""
from edx_rest_framework_extensions.auth.jwt.cookies import jwt_cookie_name
from edx_rest_framework_extensions.auth.jwt.tests.utils import (
    generate_jwt,
    generate_jwt_token,
    generate_unversioned_payload
)
from pytest import mark
from rest_framework.test import APIClient, APITestCase

from sanctions.apps.core.tests.factories import UserFactory

TEST_USERNAME = 'api_worker'
TEST_EMAIL = 'test@email.com'
TEST_PASSWORD = 'QWERTY'
TEST_FULL_NAME = 'Hermione Granger'


@mark.django_db
class APITest(APITestCase):
    """
    Base class for API Tests.
    """

    def setUp(self):
        """
        Perform operations common to all tests.
        """
        super().setUp()
        self.create_user(username=TEST_USERNAME, email=TEST_EMAIL, password=TEST_PASSWORD)
        self.client = APIClient()
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)

    def tearDown(self):
        """
        Perform common tear down operations to all tests.
        """
        # Remove client authentication credentials
        self.client.logout()
        super().tearDown()

    def create_user(self, username=TEST_USERNAME, password=TEST_PASSWORD, is_staff=False, **kwargs):
        """
        Create a test user and set its password.
        """
        self.user = UserFactory(username=username, is_staff=is_staff,  **kwargs)
        self.user.set_password(password)
        self.user.save()

    def set_jwt_cookie(self, user_id, roles=None):
        """
        Set jwt token in cookies.
        """
        if roles is None:
            roles = []

        payload = generate_unversioned_payload(self.user)
        payload.update({
            'roles': roles,
            'user_id': user_id,
        })
        jwt_token = generate_jwt_token(payload)

        self.client.cookies[jwt_cookie_name()] = jwt_token

    def generate_jwt_token_header(self, user):
        """
        Generate a valid JWT token header for authenticated requests.
        """
        return "JWT {token}".format(token=generate_jwt(user))
