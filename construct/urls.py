from django.urls import path
from .views import ConstructGame, ConstructResult
from flashcard.views import GameOver


urlpatterns = [
    path('construct/',ConstructGame.as_view(), name = 'construct'),
    path('construct_result/',ConstructResult.as_view(), name = 'construct_result'),
    path('game_over/',GameOver.as_view(), name = 'game_over'),
]