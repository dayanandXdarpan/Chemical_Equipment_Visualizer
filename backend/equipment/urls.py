from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import auth_views

router = DefaultRouter()
router.register(r'datasets', views.DatasetViewSet, basename='dataset')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', views.register_user, name='register'),
    path('auth/login/', views.login_user, name='login'),
    path('auth/logout/', views.logout_user, name='logout'),
    # Password reset endpoints
    path('auth/password-reset/request/', auth_views.request_password_reset, name='request-password-reset'),
    path('auth/password-reset/verify/', auth_views.verify_otp, name='verify-otp'),
    path('auth/password-reset/reset/', auth_views.reset_password, name='reset-password'),
    path('auth/register-enhanced/', auth_views.register, name='register-enhanced'),
    # Profile management endpoints
    path('auth/change-password/', auth_views.change_password, name='change-password'),
    path('auth/update-profile/', auth_views.update_profile, name='update-profile'),
    path('auth/delete-account/', auth_views.delete_account, name='delete-account'),
]
