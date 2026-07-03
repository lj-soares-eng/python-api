import pytest

from users.models import User
from users.serializers import (
    UserCreateSerializer,
    UserResponseSerializer,
    UserUpdateSerializer,
)


class TestUserCreateSerializer:
    def test_valid_payload(self, user_payload):
        serializer = UserCreateSerializer(data=user_payload)

        assert serializer.is_valid(), serializer.errors

    def test_rejects_short_password(self, user_payload):
        user_payload['password'] = 'short'

        serializer = UserCreateSerializer(data=user_payload)

        assert not serializer.is_valid()
        assert 'password' in serializer.errors

    def test_rejects_invalid_role(self, user_payload):
        user_payload['role'] = 'INVALID'

        serializer = UserCreateSerializer(data=user_payload)

        assert not serializer.is_valid()
        assert 'role' in serializer.errors


class TestUserUpdateSerializer:
    def test_password_optional(self):
        serializer = UserUpdateSerializer(
            data={
                'name': 'Jane Doe',
                'email': 'jane@example.com',
                'role': User.Role.USER,
            }
        )

        assert serializer.is_valid(), serializer.errors

    def test_rejects_short_password_when_provided(self):
        serializer = UserUpdateSerializer(
            data={
                'name': 'Jane Doe',
                'email': 'jane@example.com',
                'password': 'short',
                'role': User.Role.USER,
            }
        )

        assert not serializer.is_valid()
        assert 'password' in serializer.errors


@pytest.mark.django_db
class TestUserResponseSerializer:
    def test_exposes_password_hash_not_plain_password(self, created_user):
        data = UserResponseSerializer(created_user).data

        assert 'passwordHash' in data
        assert 'password' not in data
        assert data['passwordHash'].startswith('$2')

    def test_includes_expected_fields(self, created_user):
        data = UserResponseSerializer(created_user).data

        assert set(data.keys()) == {
            'id', 'name', 'email', 'passwordHash', 'role', 'created_at',
        }
