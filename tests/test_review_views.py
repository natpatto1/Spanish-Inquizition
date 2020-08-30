from django.test import TestCase
from django.contrib.auth import get_user_model
from courses.models import Levels, UserSessions, Spanish, PlayerStatus, PlayerScore
from django.urls import reverse
from flashcard.models import Answered, Questions
import json
from courses.views import LoadQuestionsMixin, InitializeMixin
from django.utils import timezone


class TestReviewViews(LoadQuestionsMixin, InitializeMixin, TestCase):
    def setUp(self):
        # self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@email.com',
            password='secret'
        )
        self.level = Levels.objects.create(
            level_number='1',
            points_threshold='100',
            description='test'
        )
        self.level2 = Levels.objects.create(
            level_number='2',
            points_threshold='200',
            description='test'
        )
        self.playerscore = PlayerScore.objects.create(
            user=self.user,
            level=self.level2,
        )
        self.question_num = PlayerStatus.objects.create(
            user=self.user,
            current_level='0',

        )
        self.spanish = Spanish.objects.create(
            spanish_phrase='testing',
            english_translation='test',
            level_number=self.level2
        )
        self.spanish2 = Spanish.objects.create(
            spanish_phrase='tester',
            english_translation='test2',
            level_number=self.level)

        self.spanish3 = Spanish.objects.create(
            spanish_phrase='tested',
            english_translation='test3',
            level_number=self.level)

        self.spanish4 = Spanish.objects.create(
            spanish_phrase='test',
            english_translation='test',
            level_number=self.level2)
        self.spanish5 = Spanish.objects.create(
            spanish_phrase='west',
            english_translation='west',
            level_number=self.level2)

        self.answeredData = Answered.objects.bulk_create(
            [Answered(user=self.user, spanish_id=self.spanish, level_int=2),
             Answered(user=self.user, spanish_id=self.spanish2, level_int=1),
             Answered(user=self.user, spanish_id=self.spanish3, level_int=1),
             Answered(user=self.user, spanish_id=self.spanish4, level_int=2),
             Answered(user=self.user, spanish_id=self.spanish5, level_int=2), ])

    def test_review_page_GET(self):
        post_response = self.client.post('/users/login/', {'username': 'testuser', 'password': 'secret'})
        self.assertEqual(post_response.url, '/')
        response = self.client.get('/review/review/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'construct.html')
        self.assertTemplateUsed(response, 'base.html')

        data = self.client.session['data']
        d = json.loads(data)
        self.assertEqual(len(d), 5)

    def test_review_page_flashcard_question_number(self):


        post_response = self.client.post('/users/login/', {'username': 'testuser', 'password': 'secret'})
        self.assertEqual(post_response.url, '/')

        self.question_num.currentQuestion = 1
        self.question_num.save()

        response = self.client.get('/review/review/')
        self.assertTemplateUsed(response, 'flashcard.html')

    def test_review_page_POST_correct(self):

        post_response = self.client.post('/users/login/', {'username': 'testuser', 'password': 'secret'})
        response = self.client.get(reverse('review'))

        data = self.client.session['data']
        d = json.loads(data)


        # Get question id for first item
        first = d[0]['fields']['spanish_id']
        question_num = Questions.objects.filter(correct_answer=str(first)).first()
        question_num = question_num.id

        post_response_review = self.client.post('/review/review/', {'question-id': [question_num],
                                                                                 'question-num': ['2'],
                                                                                 'level': ['2'],
                                                                                 'answer': [first]})


        self.assertEqual(post_response_review.status_code, 302)
        self.assertEqual(post_response_review.url, '/review/review/')





