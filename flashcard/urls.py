from django.urls import path
from .views import FlashcardGame, FlashcardResult





urlpatterns = [
    #path('index/', IndexView.as_view(), name = 'index'),
    path('flashcard/', FlashcardGame.as_view(), name='flashcard'),
    path('flashcard_result/',FlashcardResult.as_view(), name = 'flashcard_result'),

]


