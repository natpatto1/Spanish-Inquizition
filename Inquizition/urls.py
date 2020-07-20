from django.contrib import admin
from django.urls import path, include
from courses.views import UserCourses, CourseListView
from flashcard.views import FlashcardGame
from django.views.generic.base import TemplateView
from construct.views import ConstructGame
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('', include('flashcard.urls')),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('users/',include('django.contrib.auth.urls')),
    path('courses/',include('courses.urls')),
    path('flashcard/', include('flashcard.urls')),
    path('construct/',include('construct.urls')),
    path('',CourseListView.as_view(),name='home'),
    path('flashcard', FlashcardGame.as_view(), name = 'flashcards'),
    path('profile/<int:year>/<int:month>/', UserCourses.as_view(), name = 'profile_month'),



]

urlpatterns += staticfiles_urlpatterns()