from django.test import TestCase, SimpleTestCase
from .models import Levels, Spanish, PlayerScore, PlayerStatus, UserSessions
from flashcard.models import Answered
from django.contrib.auth import get_user_model
import datetime
from .views import LoadQuestionsMixin, CourseListView, UserCourses, LevelInfo, ScoreBoard
from django.urls import resolve, reverse
import json
from importlib import import_module
from django.conf import settings
from datetime import date
from django.utils import timezone

# Create your tests here.






#
#
#
# class CoursesTests (TestCase):
#     def setUp(self):
#         self.user = get_user_model().objects.create_user(
#             username='testuser',
#             email='test@email.com',
#             password='secret'
#         )
#         self.level = Levels.objects.create(
#             level_number = '1',
#             points_threshold = '100',
#             description = 'test'
#         )
#         self.userSession = UserSessions.objects.create(
#             user = self.user,
#             session = datetime.datetime.now().date(),
#         )
#
#         self.spanish = Spanish.objects.create(
#             spanish_phrase = 'test',
#             english_translation = 'test',
#             level_number = self.level
#         )
#
#         self.playerscore = PlayerScore.objects.create(
#             user = self.user,
#             level = self.level,
#         )
#         s = self.client.session
#         s.update({
#             "level_up": False,
#
#         })
#         s.save()
#
#
#     def test_home_page(self):
#         post_response = self.client.post('/users/login/', {'username': 'testuser', 'password': 'secret'})
#         self.assertEqual(post_response.url, '/')
#         response = self.client.get('/')
#         self.assertEqual(response.status_code, 200)
#
#
#     def test_home_page_post(self):
#         self.client.login(username='testuser', password='secret')
#         #Need to test that when level is selected from homepage the level info view loads
#
#
#     def test_level_info_page(self):
#         self.client.login(username='testuser', password='secret')
#         response = self.client.get('/courses/level_info/')
#         self.assertEqual(response.status_code, 200)
#
#     def test_profile_page(self):
#         self.client.login(username='testuser', password='secret')
#         response = self.client.get('/courses/profile/')
#         self.assertEqual(response.status_code, 200)
#
#     def test_scoreboard_page(self):
#         self.client.login(username='testuser', password='secret')
#         response = self.client.get('/courses/scoreboard/')
#         self.assertEqual(response.status_code, 200)
#
#     def test_profile_calendar_page(self):
#         self.client.login(username='testuser', password='secret')
#         response = self.client.get('/courses/profile/2020/1/')
#         self.assertEqual(response.status_code, 200)
#
#
