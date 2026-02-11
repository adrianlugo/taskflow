from django.urls import path
from . import views

urlpatterns = [
    path('', views.TaskListCreateView.as_view(), name='task-list-create'),
    path('<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('<int:task_id>/comments/', views.TaskCommentListCreateView.as_view(), name='task-comments'),
    path('<int:task_id>/assign/', views.assign_task, name='assign-task'),
]
