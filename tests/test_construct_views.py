from django.test import TestCase
from django.contrib.auth import get_user_model
from courses.models import Levels, UserSessions, Spanish, PlayerStatus, PlayerScore
from django.urls import reverse
from flashcard.models import Answered, Questions
import json
from courses.views import LoadQuestionsMixin, InitializeMixin
from django.utils import timezone

class ConstructTestView(TestCase, LoadQuestionsMixin, InitializeMixin):

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
        self.playerscore = PlayerScore.objects.create(
            user=self.user,
            level=self.level,
        )
        self.playerstatus = PlayerStatus.objects.create(
            user=self.user,
            current_level='0',
        )
        self.spanish = Spanish.objects.create(
            spanish_phrase='testing',
            english_translation='test',
            level_number=self.level
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
            spanish_phrase='testerer',
            english_translation='test',
            level_number=self.level)

        self.spanish5 = Spanish.objects.create(
            spanish_phrase='west',
            english_translation='west',
            level_number=self.level)

        self.answered1 = Answered.objects.create(user=self.user, spanish_id=self.spanish, level_int=1)
        self.answered2 = Answered.objects.create(user=self.user, spanish_id=self.spanish2, level_int=1)
        self.answered3 = Answered.objects.create(user=self.user, spanish_id=self.spanish3, level_int=1)
        self.answered4 = Answered.objects.create(user=self.user, spanish_id=self.spanish4, level_int=1)
        self.answered5 = Answered.objects.create(user=self.user, spanish_id=self.spanish5, level_int=1)

    def test_construct_page_GET(self):
        get_response = self.client.get('/users/login/')
        post_response = self.client.post('/users/login/', {'username': 'testuser', 'password': 'secret'})

        response = self.client.get(reverse('construct'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'construct.html')
        self.assertTemplateUsed(response, 'base.html')

        #assert question data created
        question1 = Questions.objects.filter(spanish_id= self.spanish).first()
        self.assertEqual(str(question1.spanish_id), str(self.spanish))
        question_count = Questions.objects.all().count()
        self.assertEqual(question_count, 5)

        #assert length of data
        data = self.client.session['data']
        d = json.loads(data)
        self.assertEqual(len(d),5)

        #Test data level
        self.playerstatus.refresh_from_db()
        self.assertEqual(str(d[0]['fields']['level']),str(self.playerstatus.current_level))

    def test_construct_page_POST_correct(self):
        get_response = self.client.get('/users/login/')
        post_response = self.client.post('/users/login/', {'username': 'testuser', 'password': 'secret'})
        response = self.client.get(reverse('construct'))

        data = self.client.session['data']
        d = json.loads(data)

        #Get question id for first item
        first= d[0]['fields']['spanish_id']
        question_num = Questions.objects.filter(correct_answer=str(first)).first()
        question_num = question_num.id
        print('question', question_num)

        post_response_construct = self.client.post('/construct/construct/', {'question-id': [question_num],
                                                                             'question-num': ['1'],
                                                                             'level': ['1'],
                                                                             'answer': [first]})

        self.assertEqual(post_response_construct.status_code, 302)
        self.assertEqual(post_response_construct.url, '/construct/construct/')


        spanish = Spanish.objects.filter(spanish_phrase = str(first)).first()
        answered = Answered.objects.filter(spanish_id = spanish).first()
        #As answered correctly EF should update to 2.6, quality to 5
        # repetition to 1 and review time to tomorrow and last reviewed today
        self.assertEqual(answered.repetition, 1)
        self.assertEqual(answered.ef, 2.6)
        self.assertEqual(answered.quality_value, 5)

        #check due to be reviewed tomorrow and last review is saved as today
        now = timezone.now().date()
        last_reviewed = answered.last_review_day
        reviewtime = answered.review_time.strftime("%Y-%m-%d, %H:%M")
        due = (timezone.now() + timezone.timedelta(hours=24)).strftime("%Y-%m-%d, %H:%M")
        self.assertEqual(now, last_reviewed)
        self.assertEqual(reviewtime, due)


    def test_construct_page_POST_incorrect(self):
        get_response = self.client.get('/users/login/')
        post_response = self.client.post('/users/login/', {'username': 'testuser', 'password': 'secret'})
        response = self.client.get(reverse('construct'))

        #correct_answer = Questions.objects.filter(id='1').first()
        #correct_answer = str(correct_answer.correct_answer)


        data = self.client.session['data']
        d = json.loads(data)


        #Get question id for first item
        first= d[0]['fields']['spanish_id']
        question_num = Questions.objects.filter(correct_answer=str(first)).first()
        question_num = question_num.id


        post_response_construct = self.client.post('/construct/construct/', {'question-id': [question_num],
                                                                             'question-num': ['1'],
                                                                             'level': ['1'],
                                                                             'answer': [str(first+'s')]})


        self.assertEqual(post_response_construct.status_code, 302)
        self.assertEqual(post_response_construct.url, '/construct/construct/')


        spanish = Spanish.objects.filter(spanish_phrase = str(first)).first()
        answered = Answered.objects.filter(spanish_id = spanish).first()
        #As answered incorrectly (1 letter off, therefore 4 quality) EF shouldn't update
        # repetition to 1 and review time to tomorrow and last reviewed today
        self.assertEqual(answered.repetition, 1)
        self.assertEqual(answered.ef, 2.5)
        self.assertEqual(answered.quality_value, 4)

    def test_construct_page_POST_blank(self):
        post_response = self.client.post('/users/login/', {'username': 'testuser', 'password': 'secret'})
        response = self.client.get(reverse('construct'))

        data = self.client.session['data']
        d = json.loads(data)

        first = d[0]['fields']['spanish_id']

        post_response_flashcard = self.client.post('/construct/construct/', {'question-id': ['1'],
                                                                             'question-num': ['1'],
                                                                             'level': ['1'],
                                                                             'answer': ['']})

        spanish = Spanish.objects.filter(spanish_phrase=str(first)).first()
        answered = Answered.objects.filter(spanish_id=spanish).first()
        #As timeout quality should be zero
        self.assertEqual(answered.quality_value, 0)
        self.assertEqual(answered.repetition, 0)
        self.assertEqual(answered.ef, 2.5)



    def test_construct_POST_redirect_result(self):
        get_response = self.client.get('/users/login/')
        post_response = self.client.post('/users/login/', {'username': 'testuser', 'password': 'secret'})
        response = self.client.get(reverse('construct'))

        post_response_construct = self.client.post('/construct/construct/', {'question-id': ['1'],
                                                                             'question-num': ['10'],
                                                                             'level': ['1'],
                                                                             'answer': ['test']})

        self.assertEqual(post_response_construct.status_code, 302)
        self.assertEqual(post_response_construct.url, '/result/')

    def test_construct_result_GET(self):
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















