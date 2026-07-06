import pytest
from django.contrib.auth.hashers import check_password

from users.models import User


@pytest.mark.django_db
class TestUserAPI:
    base_url = '/api/users'

    def test_list_users_empty(self, api_client):
        response = api_client.get(self.base_url)

        assert response.status_code == 200
        assert response.json() == []

    def test_create_user(self, api_client, user_payload):
        response = api_client.post(self.base_url, user_payload, format='json')

        assert response.status_code == 201
        data = response.json()
        assert data['name'] == user_payload['name']
        assert data['email'] == user_payload['email']
        assert data['role'] == user_payload['role']
        assert 'passwordHash' in data
        assert 'password' not in data
        assert data['passwordHash'].startswith('$2')

        user = User.objects.get(pk=data['id'])
        assert check_password(user_payload['password'], user.password)

    def test_create_user_validation_error(self, api_client, user_payload):
        user_payload['password'] = 'short'

        response = api_client.post(self.base_url, user_payload, format='json')

        assert response.status_code == 400

    def test_create_user_duplicate_email(self, api_client, user_payload):
        api_client.post(self.base_url, user_payload, format='json')

        response = api_client.post(self.base_url, user_payload, format='json')

        assert response.status_code == 409
        assert 'email' in response.json()['detail'].lower()

    def test_retrieve_user(self, api_client, created_user):
        response = api_client.get(f'{self.base_url}/{created_user.id}')

        assert response.status_code == 200
        data = response.json()
        assert data['id'] == created_user.id
        assert data['email'] == created_user.email
        assert 'passwordHash' in data

    def test_retrieve_user_not_found(self, api_client):
        response = api_client.get(f'{self.base_url}/999')

        assert response.status_code == 404

    def test_list_users(self, api_client, created_user):
        response = api_client.get(self.base_url)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['id'] == created_user.id

    def test_update_user(self, api_client, created_user):
        payload = {
            'name': 'Jane Smith',
            'email': 'jane.smith@example.com',
            'password': 'new-secure-pass',
            'role': User.Role.ADMIN,
        }

        response = api_client.put(
            f'{self.base_url}/{created_user.id}',
            payload,
            format='json',
        )

        assert response.status_code == 200
        data = response.json()
        assert data['name'] == payload['name']
        assert data['email'] == payload['email']
        assert data['role'] == User.Role.ADMIN

        created_user.refresh_from_db()
        assert check_password(payload['password'], created_user.password)

    def test_update_user_without_password(self, api_client, created_user):
        old_hash = created_user.password
        payload = {
            'name': 'Jane Smith',
            'email': created_user.email,
            'role': User.Role.ADMIN,
        }

        response = api_client.put(
            f'{self.base_url}/{created_user.id}',
            payload,
            format='json',
        )

        assert response.status_code == 200

        created_user.refresh_from_db()
        assert created_user.password == old_hash
        assert created_user.name == 'Jane Smith'

    def test_update_user_not_found(self, api_client):
        payload = {
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'role': User.Role.USER,
        }

        response = api_client.put(f'{self.base_url}/999', payload, format='json')

        assert response.status_code == 404

    def test_delete_user(self, api_client, created_user):
        response = api_client.delete(f'{self.base_url}/{created_user.id}')

        assert response.status_code == 204
        assert not User.objects.filter(pk=created_user.id).exists()

    def test_delete_user_not_found(self, api_client):
        response = api_client.delete(f'{self.base_url}/999')

        assert response.status_code == 404
