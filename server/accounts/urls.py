from django.urls import path
from . import views
from accounts import api

app_name = 'accounts'


# URL endppoints for the accounts app
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # REST API endpoints
    path('api/login/', api.api_login, name='api_login'),
    path('api/register/', api.api_register, name='api_register'),
    path('api/protected/', api.api_protected_data, name='api_protected_data'),
]
