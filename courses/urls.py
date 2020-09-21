from django.urls import path
from .views import UserActivity, LevelInfo, ScoreBoard, UserGuide
from django.views.generic.base import TemplateView
from django.conf.urls import url


urlpatterns = [
    path('profile/', UserActivity.as_view(), name = 'profile'),
    path('profile/<int:year>/<int:month>/', UserActivity.as_view(), name = 'profile_month'),
    path('scoreboard/', ScoreBoard.as_view(), name='scoreboard'),
    path('level_info/', LevelInfo.as_view(),name = 'level_info'),
    path('instructions/', UserGuide.as_view(), name= 'instructions'),


    ]