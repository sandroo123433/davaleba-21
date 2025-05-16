from rest_framework import mixins, viewsets
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from products.permissions import IsObjectOwnerReadOnly
from users.models import User
from users.serializers import UserSerializer, RegisterSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class UserViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

class CreateUserViewSet(CreateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class ProfileViewSet(viewsets.GenericViewSet, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsObjectOwnerReadOnly]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def perform_destroy(self, instance):
        instance.delete()

class PasswordResetRequestViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = PasswordResetSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"email": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            reset_url = request.build_absolute_uri(
                reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})
            )

            send_mail(
                "Password Reset Request",
                f"Please use the following link to reset your password: {reset_url}",
                "noreply@example.com",
                [user.email],
                fail_silently=False,
            )

            return Response(
                {"message": "Password reset link has been sent to your email."}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = PasswordResetConfirmSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('uidb64', openapi.IN_PATH, description="User ID (Base64 encoded)", type=openapi.TYPE_STRING),
            openapi.Parameter('token', openapi.IN_PATH, description="Password reset token", type=openapi.TYPE_STRING),
        ]
    )
    def create(self, request, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Password has been reset successfully."}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

