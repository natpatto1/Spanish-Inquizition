from django.contrib import admin
from django.urls import path, include
from courses.views import UserCourses, CourseListView
from flashcard.views import FlashcardGame, Result
from django.views.generic.base import TemplateView
from construct.views import ConstructGame
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static
import debug_toolbar


urlpatterns = [
    path('', include('flashcard.urls')),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('users/',include('django.contrib.auth.urls')),
    path('courses/',include('courses.urls')),
    path('flashcard/', include('flashcard.urls')),
    path('construct/',include('construct.urls')),
    path('review/',include('review.urls')),
    path('',CourseListView.as_view(),name='home'),
    path('flashcard', FlashcardGame.as_view(), name = 'flashcards'),
    path('profile/<int:year>/<int:month>/', UserCourses.as_view(), name = 'profile_month'),
    path('result/', Result.as_view(), name = 'result'),



]


urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns