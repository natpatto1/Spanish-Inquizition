from django.urls import path
from review.views import ReviewGame

urlpatterns = [
    path('review/', ReviewGame.as_view(), name='review'),]