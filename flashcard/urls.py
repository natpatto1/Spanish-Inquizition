from django.urls import path
from .views import FlashcardGame, Result





urlpatterns = [
    #path('index/', IndexView.as_view(), name = 'index'),
    path('flashcard/', FlashcardGame.as_view(), name='flashcard')
    #path('result/',Result.as_view(), name = 'result'),

]


