from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from projects.models import Project
from .models import Task

class TaskTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='password123')
        self.member = User.objects.create_user(username='member', password='password123')
        self.assignee = User.objects.create_user(username='assignee', password='password123')
        
        self.project = Project.objects.create(name='Test Project', owner=self.owner)
        self.project.members.add(self.member)
        self.project.members.add(self.assignee)
        
        self.task = Task.objects.create(
            title='Test Task',
            project=self.project,
            created_by=self.owner,
            assigned_to=self.assignee
        )
        self.task_url = f'/api/tasks/{self.task.id}/'

    def test_assignee_can_only_update_status(self):
        """Verificar que el responsable solo puede cambiar el status."""
        self.client.force_authenticate(user=self.assignee)
        
        # Intentar cambiar el título (debería fallar)
        response = self.client.patch(self.task_url, {'title': 'Hacked Title'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Intentar cambiar el status (debería funcionar)
        response = self.client.patch(self.task_url, {'status': 'en_progreso'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'en_progreso')

    def test_owner_can_update_everything(self):
        """El dueño del proyecto tiene control total."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.task_url, {'title': 'New Title', 'status': 'completada'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'New Title')

    def test_member_cannot_update_unassigned_task(self):
        """Un miembro simple no puede tocar tareas que no tiene asignadas."""
        self.client.force_authenticate(user=self.member)
        response = self.client.patch(self.task_url, {'status': 'completada'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
