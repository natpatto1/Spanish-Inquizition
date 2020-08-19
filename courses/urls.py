from django.urls import path
from .views import UserCourses, LevelInfo, ScoreBoard, UserGuide
from django.views.generic.base import TemplateView
from django.conf.urls import url


urlpatterns = [
    path('profile/', UserCourses.as_view(), name = 'profile'),
    path('profile/<int:year>/<int:month>/', UserCourses.as_view(), name = 'profile_month'),
    path('scoreboard/', ScoreBoard.as_view(), name='scoreboard'),
    path('level_info/', LevelInfo.as_view(),name = 'level_info'),
    path('instructions/', UserGuide.as_view(), name= 'instructions'),


    ]