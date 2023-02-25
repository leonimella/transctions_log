from django.urls import include, path
from rest_framework import routers
from transactions import views

router = routers.DefaultRouter()
router.register(r'', views.TransactionViewSet)

from . import views

urlpatterns = [
    path('transactions/', include(router.urls)),
]
