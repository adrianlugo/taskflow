from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Project

class ProjectTests(APITestCase):
    def setUp(self):
        # Crear dos usuarios
        self.owner = User.objects.create_user(username='owner', password='password123')
        self.other_user = User.objects.create_user(username='other', password='password123')
        
        # Crear un proyecto para el owner
        self.project = Project.objects.create(
            name='Test Project',
            owner=self.owner,
            description='A project for testing'
        )
        
        self.project_url = f'/api/projects/{self.project.id}/'

    def test_owner_can_update_project(self):
        """Verificar que el dueño puede editar su proyecto."""
        self.client.force_authenticate(user=self.owner)
        data = {'name': 'Updated Project Name'}
        response = self.client.patch(self.project_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, 'Updated Project Name')

    def test_non_owner_cannot_update_project(self):
        """Verificar que un usuario ajeno NO puede editar el proyecto."""
        self.client.force_authenticate(user=self.other_user)
        data = {'name': 'Hacker Project'}
        response = self.client.patch(self.project_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.project.refresh_from_db()
        self.assertNotEqual(self.project.name, 'Hacker Project')

    def test_non_owner_cannot_delete_project(self):
        """Verificar que un usuario ajeno NO puede eliminar el proyecto."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.project_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Project.objects.filter(id=self.project.id).exists())

    def test_project_list_contains_only_relevant_projects(self):
        """Verificar que el queryset filtra correctamente por owner/miembro."""
        # Crear otro proyecto de otro usuario
        Project.objects.create(name='Other Project', owner=self.other_user)
        
        self.client.force_authenticate(user=self.owner)
        response = self.client.get('/api/projects/')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Project')
