from django.urls import path
from . import views
from . import jwt_views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('refresh/', jwt_views.refresh_token_view, name='token_refresh'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('user/', views.user_profile, name='user-profile'),
    path('users/', views.UserListView.as_view(), name='user-list'),
]
