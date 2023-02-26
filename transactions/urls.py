from django.urls import include, path
from rest_framework import routers
from transactions import views

router = routers.DefaultRouter()
router.register(r'transactions', views.TransactionViewSet, basename='transactions')
router.register(r'users', views.UserViewSet, basename='users')

from . import views

urlpatterns = [
    path('', include(router.urls))
]
