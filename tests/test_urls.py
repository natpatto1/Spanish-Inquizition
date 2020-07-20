from django.test import TestCase
from django.urls import reverse, resolve
from courses.views import CourseListView, UserCourses, LevelInfo, ScoreBoard
from flashcard.views import FlashcardResult, FlashcardGame, GameOver
from django.contrib.auth import get_user_model
from construct.views import ConstructGame, ConstructResult


class TestUrls(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@email.com',
            password='secret'
        )

    def test_home_page_url_is_resolved(self):
        self.client.login(username='testuser', password='secret')
        url = reverse('home')
        self.assertEqual(resolve(url).func.view_class, CourseListView)

    def test_profile_page_url_is_resolved(self):
        self.client.login(username='testuser', password='secret')
        url = reverse('profile')
        self.assertEqual(resolve(url).func.view_class, UserCourses)

    def test_profile_month_page_url_is_resolved(self):
        self.client.login(username='testuser', password='secret')
        url = reverse('profile_month', args=[2020,2])
        self.assertEqual(resolve(url).func.view_class, UserCourses)


    def test_level_info_page_url_is_resolved(self):
        self.client.login(username='testuser', password='secret')
        url = reverse('level_info')
        self.assertEqual(resolve(url).func.view_class, LevelInfo)

    def test_scoreboard_page_url_is_resolved(self):
        self.client.login(username='testuser', password='secret')
        url = reverse('scoreboard')
        self.assertEqual(resolve(url).func.view_class, ScoreBoard)

class TestFlashcardUrls(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@email.com',
            password='secret'
        )

    def test_flashcard_page_url_is_resolved(self):
        self.client.login(username='testuser', password='secret')
        url = reverse('flashcard')
        self.assertEqual(resolve(url).func.view_class, FlashcardGame)

    def test_flashcard_result_page_url_is_resolved(self):
        self.client.login(username='testuser', password='secret')
        url = reverse('flashcard_result')
        self.assertEqual(resolve(url).func.view_class, FlashcardResult)

    def test_gameover_page_url_is_resolved(self):
        self.client.login(username='testuser', password='secret')
        url = reverse('game_over')
        self.assertEqual(resolve(url).func.view_class, GameOver)

class TestConstructUrls(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@email.com',
            password='secret'
        )

    def test_construct_page_url_is_resolved(self):
        self.client.login(username='testuser', password='secret')
        url = reverse('construct')
        self.assertEqual(resolve(url).func.view_class, ConstructGame)

    def test_construct_result_page_url_is_resolved(self):
        self.client.login(username='testuser', password='secret')
        url = reverse('construct_result')
        self.assertEqual(resolve(url).func.view_class, ConstructResult)