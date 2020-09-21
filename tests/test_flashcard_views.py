from django.test import TestCase
from django.contrib.auth import get_user_model
from courses.models import Levels, UserSessions, Spanish, PlayerStatus, PlayerScore
from django.urls import reverse
from flashcard.models import Answered, Questions
import json
import datetime
from courses.views import LoadQuestionsMixin, InitializeMixin
from django.utils import timezone


class TestFlashcardViews(LoadQuestionsMixin, InitializeMixin, TestCase):
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
        self.spanish = Spanish.objects.create(
            spanish_phrase='testing',
            english_translation='test',
            level_number=self.level2
        )
        self.spanish2 =Spanish.objects.create(
            spanish_phrase='tester',
            english_translation='test2',
            level_number=self.level2)

        self.spanish3 = Spanish.objects.create(
            spanish_phrase='tested',
            english_translation='test3',
            level_number=self.level2)

        self.spanish4 = Spanish.objects.create(
            spanish_phrase='test',
            english_translation='test',
            level_number=self.level2)

        self.spanish5 = Spanish.objects.create(
            spanish_phrase='west',
            english_translation='west',
            level_number=self.level2)

        self.playerscore = PlayerScore.objects.create(
            user=self.user,
            level=self.level2,
        )
        self.question_num = PlayerStatus.objects.create(
            user = self.user,
            current_level = '0',

        )

        self.answeredData = Answered.objects.bulk_create(
            [Answered(user=self.user, spanish_id = self.spanish, level_int =2),
             Answered(user=self.user, spanish_id = self.spanish2, level_int =2),
             Answered(user = self.user, spanish_id= self.spanish3, level_int =2),
             Answered(user = self.user, spanish_id= self.spanish4, level_int =2),
             Answered(user = self.user, spanish_id= self.spanish5, level_int =2),])

    def test_login_POST(self):
        get_response = self.client.get('/users/login/')
        post_response = self.client.post('/users/login/', {'username': 'testuser', 'password': 'secret'})
        self.assertEqual(post_response.url, '/')
        self.assertEqual(get_response.status_code, 200)

    def test_flashcard_page_GET(self):
        post_response = self.client.post('/users/login/', {'username': 'testuser', 'password': 'secret'})
        self.assertEqual(post_response.url, '/')
        response = self.client.get('/flashcard/flashcard/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'flashcard.html')
        self.assertTemplateUsed(response, 'base.html')

        data = self.client.session['data']
        d = json.loads(data)
        self.assertEqual(len(d), 5)

    def test_flashcard_page_POST_correct(self):
        post_response = self.client.post('/users/login/', {'username': 'testuser', 'password': 'secret'})
        response = self.client.get(reverse('flashcard'))

        data = self.client.session['data']
        d = json.loads(data)
        self.assertEqual(len(d), 5)


        # Get question id for first item
        first = d[0]['fields']['spanish_id']
        question_num = Questions.objects.filter(correct_answer=str(first)).first()
        question_num = question_num.id

        post_response_flashcard = self.client.post('/flashcard/flashcard/', {'question-id': [question_num],
                                                                             'question-num': ['1'],
                                                                             'level': ['2'],
                                                                             'answer': [first]})
        self.assertEqual(post_response_flashcard.status_code, 302)
        self.assertEqual(post_response_flashcard.url, '/flashcard/flashcard/')

        spanish = Spanish.objects.filter(spanish_phrase=str(first)).first()
        answered = Answered.objects.filter(spanish_id=spanish).first()
        # As answered correctly EF should update to 2.6, quality to 5
        # repetition to 1 and review time to tomorrow and last reviewed today
        self.assertEqual(answered.repetition, 1)
        self.assertEqual(answered.ef, 2.6)
        self.assertEqual(answered.quality_value, 5)

        # check due to be reviewed tomorrow
        now = timezone.now().date()
        last_reviewed = answered.last_review_day
        reviewtime = answered.review_time.strftime("%Y-%m-%d, %H:%M")
        due = (timezone.now() + timezone.timedelta(hours=24)).strftime("%Y-%m-%d, %H:%M")
        self.assertEqual(now, last_reviewed)
        self.assertEqual(reviewtime, due)

    def test_flashcard_page_POST_incorrect(self):
        post_response = self.client.post('/users/login/', {'username': 'testuser', 'password': 'secret'})
        response = self.client.get(reverse('flashcard'))

        data = self.client.session['data']
        d = json.loads(data)

        # Get question id for first item
        first = d[0]['fields']['spanish_id']
        question_num = Questions.objects.filter(correct_answer=str(first)).first()
        question_num = question_num.id

        post_response_flashcard = self.client.post('/flashcard/flashcard/', {'question-id': [question_num],
                                                                             'question-num': ['1'],
                                                                             'level': ['2'],
                                                                             'answer': ['wrong']})
        self.assertEqual(post_response_flashcard.status_code, 302)
        self.assertEqual(post_response_flashcard.url, '/flashcard/flashcard/')

        spanish = Spanish.objects.filter(spanish_phrase=str(first)).first()
        answered = Answered.objects.filter(spanish_id=spanish).first()
        # As answered incorrectly EF shouldn't update, quality to 1
        # repetition to 1 and review time to tomorrow and last reviewed today
        self.assertEqual(answered.repetition, 0)
        self.assertEqual(answered.ef, 2.5)
        self.assertEqual(answered.quality_value, 1)

    def test_flashcard_page_POST_timeout(self):
        post_response = self.client.post('/users/login/', {'username': 'testuser', 'password': 'secret'})
        response = self.client.get(reverse('flashcard'))

        data = self.client.session['data']
        d = json.loads(data)

        first = d[0]['fields']['spanish_id']

        post_response_flashcard = self.client.post('/flashcard/flashcard/', {'question-id': ['1'],
                                                                             'question-num': ['1'],
                                                                             'level': ['2'],
                                                                             'answer': ['timeout']})

        spanish = Spanish.objects.filter(spanish_phrase=str(first)).first()
        answered = Answered.objects.filter(spanish_id=spanish).first()
        #As timeout quality should be zero
        self.assertEqual(answered.quality_value, 0)






    def test_flashcard_result_GET(self):
        s = self.client.session
        s.update({
            "results": ['test'],
            'level_up': False})
        s.save()
        self.client.login(username='testuser', password='secret')
        response = self.client.get('/result/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'result.html')
        self.assertTemplateUsed(response, 'base.html')



