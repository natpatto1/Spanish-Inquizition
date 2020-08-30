from django.test import TestCase
from django.urls import reverse, resolve
from courses.views import CourseListView, UserCourses, LevelInfo, ScoreBoard, UserGuide
from flashcard.views import Result, FlashcardGame
from django.contrib.auth import get_user_model
from construct.views import ConstructGame
from review.views import ReviewGame


class TestUrls(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@email.com',
            password='secret'
        )

    def test_home_page_url_resolves(self):
        self.client.login(username='testuser', password='secret')
        url = reverse('home')
        self.assertEqual(resolve(url).func.view_class, CourseListView)

    def test_profile_page_url_resolves(self):
        self.client.login(username='testuser', password='secret')
        url = reverse('profile')
        self.assertEqual(resolve(url).func.view_class, UserCourses)

    def test_profile_month_page_url_resolves(self):
        self.client.login(username='testuser', password='secret')
        url = reverse('profile_month', args=[2020,2])
        self.assertEqual(resolve(url).func.view_class, UserCourses)


    def test_level_info_page_url_resolves(self):
        self.client.login(username='testuser', password='secret')
        url = reverse('level_info')
        self.assertEqual(resolve(url).func.view_class, LevelInfo)

    def test_scoreboard_page_url_resolves(self):
        self.client.login(username='testuser', password='secret')
        url = reverse('scoreboard')
        self.assertEqual(resolve(url).func.view_class, ScoreBoard)

    def test_guide_url_resolves(self):
        self.client.login(username='testuser', password='secret')
        url = reverse('instructions')
        self.assertEqual(resolve(url).func.view_class, UserGuide )


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
        url = reverse('result')
        self.assertEqual(resolve(url).func.view_class, Result)


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


class TestReviewUrls(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@email.com',
            password='secret'
        )
    def test_construct_page_url_is_resolved(self):
        self.client.login(username='testuser', password='secret')
        url = reverse('review')
        self.assertEqual(resolve(url).func.view_class, ReviewGame)
