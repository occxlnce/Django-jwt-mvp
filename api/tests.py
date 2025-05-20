from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Resource

User = get_user_model()

class AuthenticationTests(APITestCase):
    def setUp(self):
        # Create users with different roles
        self.admin_user = User.objects.create_user(
            username='Eben',
            email='eben@gmail.com',
            password='Hangwani@23',
            role=User.Role.ADMIN
        )
        self.manager_user = User.objects.create_user(
            username='Raj',
            email='ratjaji@gmail.com',
            password='Hangwani@23',
            role=User.Role.MANAGER
        )
        self.normal_user = User.objects.create_user(
            username='Thomas',
            email='thomaas@gmail.com',
            password='Hangwani@23',
            role=User.Role.USER
        )

        # Get tokens for users
        self.admin_token = self.get_token(self.admin_user)
        self.manager_token = self.get_token(self.manager_user)
        self.normal_token = self.get_token(self.normal_user)

    def get_token(self, user):
        url = reverse('token_obtain_pair')
        data = {'username': user.username, 'password': 'Hangwani@23'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data['access']

    # Test user registration
    def test_user_registration(self):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'anotherpassword',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 4) # Check if a new user is created
        new_user = User.objects.get(username='newuser')
        self.assertEqual(new_user.role, User.Role.USER) # Check default role

    # Test token obtainment
    def test_token_obtain(self):
        url = reverse('token_obtain_pair')
        data = {'username': 'Eben', 'password': 'Hangwani@23'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    # Test accessing /me/ endpoint
    def test_access_me_authenticated(self):
        url = reverse('me')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'Eben')

    def test_access_me_unauthenticated(self):
        url = reverse('me')
        self.client.credentials()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class ResourcePermissionsTests(APITestCase):
    def setUp(self):
        # Create users with different roles
        self.admin_user = User.objects.create_user(
            username='Eben',
            email='eben@gmail.com',
            password='Hangwani@23',
            role=User.Role.ADMIN
        )
        self.manager_user = User.objects.create_user(
            username='Raj',
            email='ratjaji@gmail.com',
            password='Hangwani@23',
            role=User.Role.MANAGER
        )
        self.normal_user = User.objects.create_user(
            username='Thomas',
            email='thomaas@gmail.com',
            password='Hangwani@23',
            role=User.Role.USER
        )

        # Get tokens for users
        self.admin_token = self.get_token(self.admin_user)
        self.manager_token = self.get_token(self.manager_user)
        self.normal_token = self.get_token(self.normal_user)

        # Create a resource owned by admin
        self.admin_client = self.create_authenticated_client(self.admin_token)
        resource_url = reverse('resource-list') # Using reverse for ViewSet list endpoint
        resource_data = {'name': 'Admin Resource', 'description': 'Created by admin'}
        response = self.admin_client.post(resource_url, resource_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.resource = Resource.objects.get(id=response.data['id'])

    def get_token(self, user):
        url = reverse('token_obtain_pair')
        data = {'username': user.username, 'password': 'Hangwani@23'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data['access']

    def create_authenticated_client(self, token):
        client = self.client # Use the same test client instance
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        return client

    # Test resource creation permissions
    def test_admin_can_create_resource(self):
        url = reverse('resource-list')
        data = {'name': 'New Resource by Admin', 'description': 'Description'}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Resource.objects.count(), 2) # Initial resource + new one

    def test_manager_cannot_create_resource(self):
        url = reverse('resource-list')
        data = {'name': 'New Resource by Manager', 'description': 'Description'}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.manager_token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Resource.objects.count(), 1) # No new resource created

    def test_user_cannot_create_resource(self):
        url = reverse('resource-list')
        data = {'name': 'New Resource by User', 'description': 'Description'}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.normal_token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Resource.objects.count(), 1) # No new resource created

    # Test resource list and detail permissions (all authenticated users can read)
    def test_authenticated_users_can_list_resources(self):
        url = reverse('resource-list')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.normal_token) # Test with normal user
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) # Should see the resource created in setUp

    def test_authenticated_users_can_retrieve_resource(self):
        url = reverse('resource-detail', args=[self.resource.id]) # Using reverse for ViewSet detail endpoint
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.normal_token) # Test with normal user
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.resource.name)

    def test_unauthenticated_user_cannot_read_resources(self):
        list_url = reverse('resource-list')
        detail_url = reverse('resource-detail', args=[self.resource.id])
        self.client.credentials()
        response_list = self.client.get(list_url)
        response_detail = self.client.get(detail_url)
        self.assertEqual(response_list.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response_detail.status_code, status.HTTP_401_UNAUTHORIZED)

    # Test resource update permissions
    def test_admin_can_update_resource(self):
        url = reverse('resource-detail', args=[self.resource.id])
        data = {'name': 'Admin Updated'}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        response = self.client.patch(url, data, format='json') # Using patch for partial update
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.name, 'Admin Updated')

    def test_manager_can_update_resource(self):
        url = reverse('resource-detail', args=[self.resource.id])
        data = {'name': 'Manager Updated'}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.manager_token)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.name, 'Manager Updated')

    def test_user_cannot_update_resource(self):
        url = reverse('resource-detail', args=[self.resource.id])
        data = {'name': 'User Updated'}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.normal_token)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.resource.refresh_from_db()
        self.assertNotEqual(self.resource.name, 'User Updated') # Name should not have changed

    # Test resource delete permissions
    def test_admin_can_delete_resource(self):
        # Create another resource to delete
        another_resource = Resource.objects.create(name='To Delete', description='Delete me', created_by=self.admin_user)
        self.assertEqual(Resource.objects.count(), 2) # Initial + one more

        url = reverse('resource-detail', args=[another_resource.id])
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Resource.objects.count(), 1) # Resource should be deleted
        self.assertFalse(Resource.objects.filter(id=another_resource.id).exists()) # Confirm it's gone

    def test_manager_cannot_delete_resource(self):
        url = reverse('resource-detail', args=[self.resource.id])
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.manager_token)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Resource.objects.count(), 1) # Resource should still exist

    def test_user_cannot_delete_resource(self):
        url = reverse('resource-detail', args=[self.resource.id])
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.normal_token)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Resource.objects.count(), 1) # Resource should still exist
