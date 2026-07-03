from django.contrib.auth.hashers import make_password
from django.db import IntegrityError

from users.models import User


class DuplicateEmailError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


def create_user(*, name, email, password, role):
    try:
        return User.objects.create(
            name=name,
            email=email,
            password=make_password(password),
            role=role,
        )
    except IntegrityError as exc:
        raise DuplicateEmailError('A user with this email already exists.') from exc


def update_user(user_id, *, name, email, role, password=None):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist as exc:
        raise UserNotFoundError('User not found.') from exc

    user.name = name
    user.email = email
    user.role = role
    if password:
        user.password = make_password(password)

    try:
        user.save()
    except IntegrityError as exc:
        raise DuplicateEmailError('A user with this email already exists.') from exc

    return user


def delete_user(user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist as exc:
        raise UserNotFoundError('User not found.') from exc

    user.delete()
