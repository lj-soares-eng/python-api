import pytest
from rest_framework.test import APIClient

from users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_payload():
    return {
        'name': 'Jane Doe',
        'email': 'jane@example.com',
        'password': 'secure-pass',
        'role': User.Role.USER,
    }


@pytest.fixture
def created_user(user_payload):
    from users import services

    return services.create_user(**user_payload)
