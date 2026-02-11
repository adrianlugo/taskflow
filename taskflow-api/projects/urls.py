from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProjectListCreateView.as_view(), name='project-list-create'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('<int:project_id>/members/', views.add_project_member, name='add-member'),
    path('<int:project_id>/members/<int:user_id>/', views.remove_project_member, name='remove-member'),
    path('<int:project_id>/members/list/', views.list_available_users, name='list-users'),
]
