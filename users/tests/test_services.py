import pytest
from django.contrib.auth.hashers import check_password

from users import services
from users.models import User


@pytest.mark.django_db
class TestCreateUser:
    def test_creates_user_with_hashed_password(self, user_payload):
        user = services.create_user(**user_payload)

        assert user.id is not None
        assert user.name == user_payload['name']
        assert user.email == user_payload['email']
        assert user.role == User.Role.USER
        assert user.created_at is not None
        assert check_password(user_payload['password'], user.password)

    def test_raises_on_duplicate_email(self, user_payload):
        services.create_user(**user_payload)

        with pytest.raises(services.DuplicateEmailError):
            services.create_user(**user_payload)


@pytest.mark.django_db
class TestUpdateUser:
    def test_updates_fields(self, created_user):
        updated = services.update_user(
            created_user.id,
            name='Jane Smith',
            email='jane.smith@example.com',
            role=User.Role.ADMIN,
        )

        assert updated.name == 'Jane Smith'
        assert updated.email == 'jane.smith@example.com'
        assert updated.role == User.Role.ADMIN

    def test_rehashes_password_when_provided(self, created_user):
        old_hash = created_user.password

        updated = services.update_user(
            created_user.id,
            name=created_user.name,
            email=created_user.email,
            role=created_user.role,
            password='new-secure-pass',
        )

        assert updated.password != old_hash
        assert check_password('new-secure-pass', updated.password)

    def test_keeps_password_when_not_provided(self, created_user):
        old_hash = created_user.password

        updated = services.update_user(
            created_user.id,
            name='Updated Name',
            email=created_user.email,
            role=created_user.role,
        )

        assert updated.password == old_hash

    def test_raises_when_user_not_found(self):
        with pytest.raises(services.UserNotFoundError):
            services.update_user(
                999,
                name='Nobody',
                email='nobody@example.com',
                role=User.Role.USER,
            )

    def test_raises_on_duplicate_email(self, user_payload, created_user):
        other = services.create_user(
            name='Other User',
            email='other@example.com',
            password='secure-pass',
            role=User.Role.USER,
        )

        with pytest.raises(services.DuplicateEmailError):
            services.update_user(
                other.id,
                name=other.name,
                email=created_user.email,
                role=other.role,
            )


@pytest.mark.django_db
class TestDeleteUser:
    def test_deletes_user(self, created_user):
        user_id = created_user.id

        services.delete_user(user_id)

        assert not User.objects.filter(pk=user_id).exists()

    def test_raises_when_user_not_found(self):
        with pytest.raises(services.UserNotFoundError):
            services.delete_user(999)
