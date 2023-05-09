"""
Tests for tasks APIs.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Task

from task.serializers import TaskSerializer

TASKS_URL = reverse('task:task-list')


def detail_url(task_id):
    """Create and return a task detail URL."""
    return reverse('task:task-detail', args=[task_id])


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


def create_task(user, **params):
    """Create and return a sample task."""
    defaults = {
        'title': 'Sample task title',
        'description': 'Sample task description.',
    }
    defaults.update(params)

    task = Task.objects.create(user=user, **defaults)
    return task


class PublicTaskAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(TASKS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTaskApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(self.user)

    def test_retrieve_tasks(self):
        """Test retrieving a list of tasks."""
        create_task(user=self.user)
        create_task(user=self.user)

        res = self.client.get(TASKS_URL)

        tasks = Task.objects.all().order_by('-id')
        serializer = TaskSerializer(tasks, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_task_list_limited_to_user(self):
        """Test list of tasks is limited to authenticated user."""
        other_user = create_user(username='otheruser', password='testpass123')
        create_task(user=other_user)
        create_task(user=self.user)

        res = self.client.get(TASKS_URL)

        tasks = Task.objects.filter(user=self.user)
        serializer = TaskSerializer(tasks, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_task_detail(self):
        """Test get task detail."""
        task = create_task(user=self.user)

        url = detail_url(task.id)
        res = self.client.get(url)

        task = Task.objects.get(id=task.id)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for k, v in res.data.items():
            self.assertEqual(getattr(task, k), v)
        self.assertEqual(task.user, self.user)

    def test_create_task(self):
        """Test creating a task."""

        payload = {
            'title': 'Sample task title',
            'description': 'Sample task description.',
        }
        res = self.client.post(TASKS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(task, k), v)
        self.assertEqual(task.user, self.user)

    def test_partial_update(self):
        """Test partial update of a task."""
        original_description = 'Sample task description'
        task = create_task(
            user=self.user,
            title='Sample task title',
            description=original_description
        )

        payload = {'title': 'New task title'}
        url = detail_url(task.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.title, payload['title'])
        self.assertEqual(task.description, original_description)
        self.assertEqual(task.user, self.user)

    def test_full_update(self):
        """Test full update of a task."""
        task = create_task(
            user=self.user,
            title='Sample task title',
            description='Sample task description',
        )

        payload = {
            'title': 'New task title',
            'description': 'New task description.',
        }

        url = detail_url(task.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(task, k), v)
        self.assertEqual(task.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the task user results in an error."""
        new_user = create_user(username='user2', password='test123')
        task = create_task(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(task.id)
        self.client.patch(url, payload)

        task.refresh_from_db()
        self.assertEqual(task.user, self.user)

    def test_delete_task(self):
        """Test deleting a task successful."""
        task = create_task(user=self.user)

        url = detail_url(task.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=task.id).exists())

    def test_task_other_users_task_error(self):
        """Test trying to delete another users task gives error."""
        new_user = create_user(username='user2', password='test123')
        task = create_task(user=new_user)

        url = detail_url(task.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Task.objects.filter(id=task.id).exists())
