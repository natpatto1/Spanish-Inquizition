from django.urls import path
from .views import ConstructGame, ConstructResult



urlpatterns = [
    path('construct/',ConstructGame.as_view(), name = 'construct'),
    path('construct_result/',ConstructResult.as_view(), name = 'construct_result'),
]