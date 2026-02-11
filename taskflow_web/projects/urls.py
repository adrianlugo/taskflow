from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='list'),
    path('create/', views.ProjectCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', views.ProjectUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='delete'),
    # URLs que coinciden exactamente con la API
    path('<int:project_id>/members/', views.AddProjectMemberView.as_view(), name='add_member'),
    path('<int:project_id>/members/<int:user_id>/', views.RemoveProjectMemberView.as_view(), name='remove_member'),
]
