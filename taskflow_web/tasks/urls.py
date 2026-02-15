from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.TaskListView.as_view(), name='list'),
    path('create/', views.TaskCreateView.as_view(), name='create'),
    path('<int:pk>/', views.TaskDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', views.TaskUpdateView.as_view(), name='update'),
    path('<int:pk>/complete/', views.TaskCompleteView.as_view(), name='complete'),
    path('<int:pk>/status/', views.TaskChangeStatusView.as_view(), name='status'),
    path('<int:pk>/delete/', views.TaskDeleteView.as_view(), name='delete'),
]
