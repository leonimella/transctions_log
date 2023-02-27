from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from .models import User, Transaction
from .views import UserViewSet

class UsersTestCase(APITestCase):
    def test_should_create_new_user(self):
        user = {'username': 'test_user', 'email': 'test_user@example.com', 'password': '123456789'}

        response = self.client.post('/users/', data=user, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

    def test_should_error_when_username_is_taken(self):
        userA = {'username': 'test_user', 'email': 'test_user@example.com', 'password': '123456789'}
        userB = {'username': 'test_user', 'email': 'test_user02@example.com', 'password': '123456789'}

        response = self.client.post('/users/', data=userA, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

        response = self.client.post('/users/', data=userB, format='json')
        [error] = response.data.get('username', [''])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(error, 'A user with that username already exists.')
        self.assertEqual(error.code, 'unique')

    def test_should_error_when_email_is_taken(self):
        userA = {'username': 'test_user', 'email': 'test_user@example.com', 'password': '123456789'}
        userB = {'username': 'test_user02', 'email': 'test_user@example.com', 'password': '123456789'}

        response = self.client.post('/users/', data=userA, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

        response = self.client.post('/users/', data=userB, format='json')
        [error] = response.data.get('email', [''])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(error, 'This field must be unique.')
        self.assertEqual(error.code, 'unique')

    def test_should_error_when_password_is_too_short(self):
        user = {'username': 'test_user', 'email': 'test_user@example.com', 'password': '123'}

        response = self.client.post('/users/', data=user, format='json')
        [error] = response.data.get('password', [''])

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(error, 'This password is too short. It must contain at least 8 characters.')
        self.assertEqual(error.code, 'password_too_short')

    def test_should_return_body(self):
        user = {'username': 'test_user', 'email': 'test_user@example.com', 'password': '123456789'}

        response = self.client.post('/users/', data=user, format='json')
        username = response.data.get('username', False)
        email = response.data.get('email', False)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual('test_user', username)
        self.assertEqual('test_user@example.com', email)

    def test_balance_should_return_correct_user_balance(self):
        # Making the User
        userData = {'username': 'test_user', 'email': 'test_user@example.com', 'password': '123456789'}
        response = self.client.post('/users/', data=userData, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(pk=1)

        # Creating deposits Transactions
        expectedBalance = 0
        for i in range(5):
            depositType = Transaction.TransactionTypes.DEPOSIT
            t = Transaction(type=depositType, value=1000, merchant=None, user=user)
            t.save()

            expectedBalance += 1000

        # Preparing authenticated balance request
        factory = APIRequestFactory()
        view = UserViewSet.as_view({'get': 'balance'})
        request = factory.get('/users/balance', format='json')
        force_authenticate(request=request, user=user)

        # Asserting expected balance
        response = view(request)
        balance = response.data.get('balance', None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(balance, expectedBalance)

        # Creating Withdraw Transactions
        for i in range(2):
            depositType = Transaction.TransactionTypes.WITHDRAW
            t = Transaction(type=depositType, value=200, merchant=None, user=user)
            t.save()

            expectedBalance -= 200

        # Asserting expected balance
        response = view(request)
        balance = response.data.get('balance', None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(balance, expectedBalance)

        # Creating Withdraw Expenses
        for i in range(2):
            depositType = Transaction.TransactionTypes.WITHDRAW
            t = Transaction(type=depositType, value=500, merchant='Merchant One', user=user)
            t.save()

            expectedBalance -= 500

        # Asserting expected balance
        response = view(request)
        balance = response.data.get('balance', None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(balance, expectedBalance)


    def test_should_authenticate_and_return_token(self):
        user = {'username': 'test_user', 'email': 'test_user@example.com', 'password': '123456789'}
        response = self.client.post('/users/', data=user, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post('/authenticate', data={'username': 'test_user', 'password': '123456789'}, format='json')
        token = response.data.get('token', None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(token)

    def test_should_raise_when_invalid_credentials(self):
        user = {'username': 'test_user', 'email': 'test_user@example.com', 'password': '123456789'}
        response = self.client.post('/users/', data=user, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post('/authenticate', data={'username': 'test_user', 'password': '987654321'}, format='json')
        [error] = response.data.get('non_field_errors', [''])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(error, 'Unable to log in with provided credentials.')
        self.assertEqual(error.code, 'authorization')

class TransactionsTestCase(APITestCase):
    def test_should(self):
        self.assertEqual(True, False)
