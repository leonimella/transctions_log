from datetime import datetime, timedelta
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from .models import User, Transaction
from .views import UserViewSet, TransactionViewSet

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

    def test_should_return_correct_user_balance(self):
        # Making the User
        userData = {'username': 'test_user', 'email': 'test_user@example.com', 'password': '123456789'}
        response = self.client.post('/users/', data=userData, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='test_user')
        now = datetime.now()

        # Creating deposits Transactions
        expectedBalance = 0
        for i in range(5):
            depositType = Transaction.TransactionTypes.DEPOSIT
            t = Transaction(type=depositType,
                            value=1000,
                            merchant=None,
                            user=user,
                            created_at=now)
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
            t = Transaction(type=depositType,
                            value=200,
                            merchant=None,
                            user=user,
                            created_at=now)
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
            t = Transaction(type=depositType,
                            value=500,
                            merchant=None,
                            user=user,
                            created_at=now)
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
    DEPOSIT = Transaction.TransactionTypes.DEPOSIT
    WITHDRAW = Transaction.TransactionTypes.WITHDRAW
    EXPENSE = Transaction.TransactionTypes.EXPENSE

    def setUp(self) -> None:
        Jane = User(username='janedoe', email='jane.doe@example.com', password='123456789')
        John = User(username='johndoe', email='john.doe@example.com', password='123456789')
        Jane.save()
        John.save()

    def makePostRequest(self, path, data, user):
        factory = APIRequestFactory()
        view = TransactionViewSet.as_view({'post': 'create'})
        request = factory.post(path=path, data=data, format='json')
        force_authenticate(request=request, user=user)
        return view(request)

    def makeGetRequest(self, path, action, user):
        factory = APIRequestFactory()
        view = TransactionViewSet.as_view({'get': action})
        request = factory.get(path=path, format='json')
        force_authenticate(request=request, user=user)
        return view(request)

    def create_transactions(self, user, transactions=None):
        if transactions is None:
            transactions = [
                {'type': self.DEPOSIT, 'merchant': None, 'value': 1000},
                {'type': self.WITHDRAW, 'merchant': None, 'value': 500},
                {'type': self.EXPENSE, 'merchant': 'Merchant Name', 'value': 500}
            ]

        for t in transactions:
            self.makePostRequest('/transactions/', t, user)

        return len(transactions)

    def test_should_create_new_transaction(self):
        jane = User.objects.get(username='janedoe')

        # Creating a DEPOSIT Transaction
        tData = {'type': self.DEPOSIT, 'merchant': None, 'value': 1000}
        response = self.makePostRequest('/transactions/', tData, jane)
        tType = response.data.get('type', None)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(tType, self.DEPOSIT)
        self.assertEqual(Transaction.objects.count(), 1)

        # Creating a WITHDRAW Transaction
        tData = {'type': self.WITHDRAW, 'merchant': None, 'value': 200}
        response = self.makePostRequest('/transactions/', tData, jane)
        tType = response.data.get('type', None)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(tType, self.WITHDRAW)
        self.assertEqual(Transaction.objects.count(), 2)

        # Creating a EXPENSE Transaction
        tData = {'type': self.EXPENSE, 'merchant': 'Merchant One', 'value': 200}
        response = self.makePostRequest('/transactions/', tData, jane)
        tType = response.data.get('type', None)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(tType, self.EXPENSE)
        self.assertEqual(Transaction.objects.count(), 3)

    def test_should_list_transactions_separate_by_users(self):
        jane = User.objects.get(username='janedoe')
        john = User.objects.get(username='johndoe')

        janeCount = self.create_transactions(jane)
        johnCount = self.create_transactions(john)
        self.assertEqual(Transaction.objects.count(), janeCount + johnCount)

        janeResponse = self.makeGetRequest('/transactions/', 'list', jane)
        johnResponse = self.makeGetRequest('/transactions/', 'list', john)

        # Asserting transaction count is correct
        self.assertEqual(janeResponse.status_code, status.HTTP_200_OK)
        self.assertEqual(johnResponse.status_code, status.HTTP_200_OK)
        self.assertEqual(janeResponse.data['count'], janeCount)
        self.assertEqual(johnResponse.data['count'], johnCount)

        # Asserting transaction's user doesn't include other users
        janeUserIds = [r['user'] for r in janeResponse.data['results']]
        johnUserIds = [r['user'] for r in johnResponse.data['results']]
        self.assertEqual(False, True if john.id in janeUserIds else False)
        self.assertEqual(False, True if jane.id in johnUserIds else False)

    def test_should_list_by_type(self):
        jane = User.objects.get(username='janedoe')
        transactions = [
            {'type': self.DEPOSIT, 'merchant': None, 'value': 1000},
            {'type': self.DEPOSIT, 'merchant': None, 'value': 1000},
            {'type': self.WITHDRAW, 'merchant': None, 'value': 500},
            {'type': self.EXPENSE, 'merchant': 'Merchant A', 'value': 200},
            {'type': self.EXPENSE, 'merchant': 'Merchant B', 'value': 200},
            {'type': self.EXPENSE, 'merchant': 'Merchant C', 'value': 200}
        ]
        self.create_transactions(jane, transactions)

        filterByDeposit = f'/transactions/?type={Transaction.TransactionTypes.DEPOSIT}'
        depositResponse = self.makeGetRequest(filterByDeposit, 'list', jane)

        filterByWithdraw = f'/transactions/?type={Transaction.TransactionTypes.WITHDRAW}'
        withdrawResponse = self.makeGetRequest(filterByWithdraw, 'list', jane)

        filterByExpense = f'/transactions/?type={Transaction.TransactionTypes.EXPENSE}'
        expenseResponse = self.makeGetRequest(filterByExpense, 'list', jane)

        # Asserting correct call to API
        self.assertEqual(depositResponse.status_code, status.HTTP_200_OK)
        self.assertEqual(withdrawResponse.status_code, status.HTTP_200_OK)
        self.assertEqual(expenseResponse.status_code, status.HTTP_200_OK)

        # Asserting correct result count
        self.assertEqual(depositResponse.data['count'], 2)
        self.assertEqual(withdrawResponse.data['count'], 1)
        self.assertEqual(expenseResponse.data['count'], 3)

        # Asserting proper results types
        depositTypes = [r['type'] for r in depositResponse.data['results']]
        withdrawTypes = [r['type'] for r in withdrawResponse.data['results']]
        expenseTypes = [r['type'] for r in expenseResponse.data['results']]

        self.assertEqual(True, True if Transaction.TransactionTypes.DEPOSIT in depositTypes else False, 'Found wrong type in response')
        self.assertEqual(True, True if Transaction.TransactionTypes.WITHDRAW in withdrawTypes else False, 'Found wrong type in response')
        self.assertEqual(True, True if Transaction.TransactionTypes.EXPENSE in expenseTypes else False, 'Found wrong type in response')

    def test_should_list_by_merchant(self):
        jane = User.objects.get(username='janedoe')
        transactions = [
            {'type': self.DEPOSIT, 'merchant': None, 'value': 5000},
            {'type': self.EXPENSE, 'merchant': 'Merchant A', 'value': 100},
            {'type': self.EXPENSE, 'merchant': 'Merchant B', 'value': 200},
            {'type': self.EXPENSE, 'merchant': 'Merchant B', 'value': 200},
            {'type': self.EXPENSE, 'merchant': 'Merchant C', 'value': 300},
            {'type': self.EXPENSE, 'merchant': 'Merchant C', 'value': 500},
            {'type': self.EXPENSE, 'merchant': 'Merchant C', 'value': 250}
        ]
        self.create_transactions(jane, transactions)

        filterByMercA = '/transactions/?merchant=Merchant%20A'
        mercAResponse = self.makeGetRequest(filterByMercA, 'list', jane)

        filterByMercB = '/transactions/?merchant=Merchant%20B'
        mercBResponse = self.makeGetRequest(filterByMercB, 'list', jane)

        filterByMercC = '/transactions/?merchant=Merchant%20C'
        mercCResponse = self.makeGetRequest(filterByMercC, 'list', jane)

        # Asserting correct call to API
        self.assertEqual(mercAResponse.status_code, status.HTTP_200_OK)
        self.assertEqual(mercBResponse.status_code, status.HTTP_200_OK)
        self.assertEqual(mercCResponse.status_code, status.HTTP_200_OK)

        # Asserting correct result count
        self.assertEqual(mercAResponse.data['count'], 1)
        self.assertEqual(mercBResponse.data['count'], 2)
        self.assertEqual(mercCResponse.data['count'], 3)

        # Asserting proper results merchants
        mercA = [r['merchant'] for r in mercAResponse.data['results']]
        mercB = [r['merchant'] for r in mercBResponse.data['results']]
        mercC = [r['merchant'] for r in mercCResponse.data['results']]

        self.assertEqual(True, True if 'Merchant A' in mercA else False, 'Found wrong merchant in response')
        self.assertEqual(True, True if 'Merchant B' in mercB else False, 'Found wrong merchant in response')
        self.assertEqual(True, True if 'Merchant C' in mercC else False, 'Found wrong merchant in response')

    def test_should_list_by_time_range(self):
        jane = User.objects.get(username='janedoe')
        now = datetime.now()

        # Creating 10 Deposits transactions
        # transactions id 1 and 10 will be 10 days apart
        for i in range(1, 11):
            createdAt = now - timedelta(days=11-i)
            type = Transaction.TransactionTypes.DEPOSIT
            newTransaction = Transaction(type=type,
                                         value=100,
                                         user=jane,
                                         created_at=createdAt)
            newTransaction.save()

        fromParam = (now - timedelta(days=10)).strftime('%Y-%m-%d')
        toTwoDays = (now - timedelta(days=8)).strftime('%Y-%m-%d')
        toFiveDays = (now - timedelta(days=5)).strftime('%Y-%m-%d')
        toEightDays = (now - timedelta(days=2)).strftime('%Y-%m-%d')

        twoDaysRange = f'/transactions/?from={fromParam}&to={toTwoDays}'
        twoDaysResponse = self.makeGetRequest(twoDaysRange, 'list', jane)

        fiveDaysRange = f'/transactions/?from={fromParam}&to={toFiveDays}'
        fiveDaysResponse = self.makeGetRequest(fiveDaysRange, 'list', jane)

        eightDaysRange = f'/transactions/?from={fromParam}&to={toEightDays}'
        eightDaysResponse = self.makeGetRequest(eightDaysRange, 'list', jane)

        # Asserting correct call to API
        self.assertEqual(twoDaysResponse.status_code, status.HTTP_200_OK)
        self.assertEqual(fiveDaysResponse.status_code, status.HTTP_200_OK)
        self.assertEqual(eightDaysResponse.status_code, status.HTTP_200_OK)

        # Asserting correct result count
        self.assertEqual(twoDaysResponse.data['count'], 2)
        self.assertEqual(fiveDaysResponse.data['count'], 5)
        self.assertEqual(eightDaysResponse.data['count'], 8)

    def test_should_error_when_not_list_by_range_with_from_or_to(self):
        jane = User.objects.get(username='janedoe')
        transactions = [
            {'type': self.DEPOSIT, 'merchant': None, 'value': 5000},
            {'type': self.DEPOSIT, 'merchant': None, 'value': 100},
            {'type': self.DEPOSIT, 'merchant': None, 'value': 200},
        ]
        self.create_transactions(jane, transactions)

        onlyFrom = '/transactions/?from=2023-02-24'
        fromResponse = self.makeGetRequest(onlyFrom, 'list', jane)
        fromError = fromResponse.data['error']

        onlyTo = '/transactions/?to=2023-02-28'
        toResponse = self.makeGetRequest(onlyTo, 'list', jane)
        toError = toResponse.data['error']

        wrongOrder = '/transactions/?from=2023-02-28&to=2023-02-20'
        wrongResponse = self.makeGetRequest(wrongOrder, 'list', jane)
        wrongError = wrongResponse.data['error']

        self.assertEqual(fromResponse.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(toResponse.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(wrongResponse.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(fromError, 'you must define both \'from\' and \'to\' parameters')
        self.assertEqual(toError, 'you must define both \'from\' and \'to\' parameters')
        self.assertEqual(wrongError, '\'from\' parameter is ahead of \'to\'')

    def test_should_error_when_creating_expense_transaction_without_balance(self):
        jane = User.objects.get(username='janedoe')

        # Creating a DEPOSIT of 1000 units
        deposit = {'type': self.DEPOSIT, 'merchant': None, 'value': 1000}
        self.makePostRequest('/transactions/', deposit, jane)

        # Spending 900 units
        expense = {'type': self.EXPENSE, 'merchant': 'Merchant A', 'value': 900}
        response = self.makePostRequest('/transactions/', expense, jane)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Spending another 200 units, going over Jane's balance of 1000 units
        expense = {'type': self.EXPENSE, 'merchant': 'Merchant B', 'value': 200}
        errorResponse = self.makePostRequest('/transactions/', expense, jane)
        errorMessage = errorResponse.data['error']

        self.assertEqual(errorResponse.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(errorMessage, 'insufficient balance')

    def test_should_error_when_creating_withdraw_transaction_without_balance(self):
        jane = User.objects.get(username='janedoe')

        # Creating a DEPOSIT of 1000 units
        deposit = {'type': self.DEPOSIT, 'merchant': None, 'value': 1000}
        self.makePostRequest('/transactions/', deposit, jane)

        # Spending 900 units
        expense = {'type': self.WITHDRAW, 'merchant': None, 'value': 900}
        response = self.makePostRequest('/transactions/', expense, jane)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Spending another 200 units, going over Jane's balance of 1000 units
        expense = {'type': self.WITHDRAW, 'merchant': None, 'value': 200}
        errorResponse = self.makePostRequest('/transactions/', expense, jane)
        errorMessage = errorResponse.data['error']

        self.assertEqual(errorResponse.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(errorMessage, 'insufficient balance')
