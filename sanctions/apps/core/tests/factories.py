"""
Factoryboy factories.
"""

import logging

import factory

from sanctions.apps.core.models import User

USER_PASSWORD = 'password'

# Silence faker locale warnings
logging.getLogger("faker").setLevel(logging.ERROR)


class UserFactory(factory.django.DjangoModelFactory):
    """
    Test factory for the `User` model.
    """
    id = factory.Sequence(lambda n: n + 1)
    lms_user_id = factory.Sequence(lambda n: n + 1)
    username = factory.Faker('user_name')
    password = factory.PostGenerationMethodCall('set_password', USER_PASSWORD)
    email = factory.Faker('email')
    is_staff = False
    is_superuser = False

    class Meta:
        model = User
