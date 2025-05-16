from django.urls import path, include
from rest_framework_nested import routers
from users.views import UserViewSet, CreateUserViewSet, ProfileViewSet, PasswordResetRequestViewSet, PasswordResetConfirmViewSet

router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('register', CreateUserViewSet, basename='register')
router.register('profile', ProfileViewSet, basename='profile')
router.register('password_reset', PasswordResetRequestViewSet, basename='password_reset')

urlpatterns = [
    path('', include(router.urls)),
    path('password_reset_confirm/<uidb64>/<token>/', PasswordResetConfirmViewSet.as_view({'post': 'create'}), name='password_reset_confirm'),
]