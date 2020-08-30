from django.urls import path
from .views import ConstructGame


urlpatterns = [
    path('construct/',ConstructGame.as_view(), name = 'construct'),
]