from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from users.models import EmailVerificationCode
from django.utils import timezone
from django.models import EmailVerificationCode



User = get_user_model()

class RegistrationViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.resgister_usr = reverse('register-list')
        self.user.data = {
            "username":"testuser",
            "email":"test@example.com",
            "password":"strongpassword123",
            "password2":"strongpassword123",
            "firstname":"Test",
            "firstname":"User",
            "phone_number":"+995571173451"


        }
    def test_user_registracion_success(self):
        response = self.client.post(self.resgister_usr, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(email=self.user_data['email']).exist())
        user = User.objects.get(email=self.user_data['email'])
        self.assertFalse(user.is_active)
        self.assertTrue(EmailVerificationCode.objects.filter(user=user).exists())

    def test_user_registration_password_mismatch(self):
        self.user_data['password2'] = 'differentpassword123'
        response = self.client.post(self.resgister_usr, self.user_data, format='json')
        self.assertEqual(respomse.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password',response.data)
        self.assertFalse(User.objects.filter(email=self.user_data['email']).exist())


    def test_user_registration_duplicae_email(self):
        User.objects.create_user(
            username='existinguser',
            email=self.user_data['email'],
            password='password123'
        )  
        respomse = self.client.post (self.resgister_usr, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)


class EmailVerificationCode(TestCase):
    def setUp(self):
        self.client = APIClient()


        self.user = User.objects.create_user(
            username = 'testuser',
            email = 'test@example.com',
            password = 'password123',
            is_active = False
        )

        self.confirm_url = revense('register-confirm-code')
        

        self.verification_code = EmailVerificationCode.objects.create(
            user = self.user,
            code = '123456',
            created_at=timezone.now()
        )
    

    def test_successful_verification(self):
        data = {
            "email":"test@example.com",
            "code":"123456"
        }

        response = self.client.post(self.confrim_url, data, format='json')
        self.assertTrue(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)


    def test_invalid_code(self):
        data = {
            "email":"test@example.com",
            "code":"123456"
        }

        response = self.client.post(self.confirm_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)



    def test_expired_code(self):
        self.verification_code.created_at = timezone.now() - timezone.timedelta(hours=24)
        data= { 
            "email":"test@example.com",
            "code":"123456"
        }
        response = self.client.post(self.confirm_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refreh_from_db()
        self.assertFalse(self.user.is_active)


class AuthenticationTest(TestCase):
    def setUp(
        self.client = APIClient()
        self.login_url = reverse('token_obyain_pair')
        self.user_detail_url = reverse('category-list')


        self.user = User.objects.create_user(
            username = 'authuser',
            email='auth@example.com',
            password='auth123password'
        )
    )

    def test_login_valid_credentails(self):
        data = {
            "emai":"auth@example.com",
            "password":"auth123password"
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.satus_code, satus.HTTP_200_OK)
        self.assertIn('acess', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentails(self):
        data = {
            "emai":"auth@example.com",
            "password":"auth123password"
        }
        response = self.client.post(self.login_url, data, formay='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_access_protected_resourse(self):
        data = {
            "emai":"auth@example.com",
            "password":"auth123password"
        }   

        login_response = self.client.post(self.login_url, data, format='json')
        toke = logint_response.data['access']
        self.client.credential(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(self.user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    


    def test_access_protected_resourse_without_auth(self):
        response = self.client.get(self.user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)