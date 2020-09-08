from django.test import TestCase
from django.contrib.auth import get_user_model
from courses.models import Levels, UserSessions, Spanish, PlayerStatus, PlayerScore
from django.urls import reverse
from flashcard.models import Answered, Questions
import json
import datetime
from courses.views import LoadQuestionsMixin, InitializeMixin
from django.utils import timezone
from datetime import date, timedelta


class TestCourseViews(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@email.com',
            password='secret'
        )
        self.level = Levels.objects.create(
            level_number = '1',
            points_threshold = '100',
            description = 'test'
        )
        self.level2 = Levels.objects.create(
            level_number='2',
            points_threshold='200',
            description='test2'
        )
        self.today = timezone.now().date()
        self.userSession = UserSessions.objects.create(
            user = self.user,
            session = self.today
        )
        self.spanish = Spanish.objects.create(
            spanish_phrase = 'testing',
            english_translation = 'test',
            level_number = self.level
        )
        self.spanish2 =Spanish.objects.create(
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
            level_number=self.level)

        self.spanish5 = Spanish.objects.create(
            spanish_phrase='west',
            english_translation='west',
            level_number=self.level)

        self.spanish6 = Spanish.objects.create(
            spanish_phrase = 'when',
            english_translation='when',
            level_number=self.level2
        )
        self.spanish7 = Spanish.objects.create(
            spanish_phrase='two',
            english_translation='two',
            level_number=self.level2
        )
        self.spanish8 = Spanish.objects.create(
            spanish_phrase='strong',
            english_translation='strong',
            level_number=self.level2
        )
        self.spanish9 = Spanish.objects.create(
            spanish_phrase='stronger',
            english_translation='stronger',
            level_number=self.level2
        )
        self.playerscore = PlayerScore.objects.create(
            user = self.user,
            level = self.level,
        )
        self.answered = Answered.objects.create(
            user=self.user,
            spanish_id=self.spanish,
            level_int = 1,
        )
        self.answered2 = Answered.objects.create(
            user=self.user,
            spanish_id=self.spanish2,
            level_int=1,
        )
        self.answered3 = Answered.objects.create(
            user=self.user,
            spanish_id=self.spanish3,
            level_int=1,
        )
        self.answered4 = Answered.objects.create(
            user=self.user,
            spanish_id=self.spanish4,
            level_int=1,
        )
        self.answered5 = Answered.objects.create(
            user=self.user,
            spanish_id=self.spanish5,
            level_int=1,
        )
        self.answered6 = Answered.objects.create(
        user=self.user,
        spanish_id=self.spanish6,
        repetition=4,
        level_int=2,
        review_time=self.today + timezone.timedelta(hours=730)
        )
        self.answered7 = Answered.objects.create(
        user=self.user,
        spanish_id=self.spanish7,
        repetition=4,
        level_int=2,
        review_time=self.today + timezone.timedelta(hours=730)
        )
        self.answered8 = Answered.objects.create(
        user=self.user,
        spanish_id=self.spanish8,
        repetition=4,
        level_int=2,
        review_time=self.today + timezone.timedelta(hours=730)
        )
        self.answered9 = Answered.objects.create(
        user=self.user,
        spanish_id=self.spanish9,
        repetition=4,
        level_int=2,
        review_time=self.today + timezone.timedelta(hours=730)
        )

    def test_homepage_GET(self):
        self.client.login(username='testuser', password='secret')
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertTemplateUsed(response, 'base.html')

        #test level up session data is set
        self.assertEqual(self.client.session['level_up'], False)

    def test_homepage_streak(self):
        self.client.login(username='testuser', password='secret')
        response = self.client.get(reverse('home'))
        self.playerscore.refresh_from_db()


        #Streak should calculate as 1 as only one instance in user session
        self.assertEqual(self.playerscore.day_streak,1)


    def test_homepage_GET_level_up(self):
        self.playerscore.current_level_score = 501
        self.playerscore.save()

        self.client.login(username='testuser', password='secret')
        response = self.client.get(reverse('home'))

        self.playerscore.refresh_from_db()

        self.assertEqual(str(self.playerscore.level), str(self.level2))

    def test_homepage_GET_strength_context(self):
        self.client.login(username='testuser', password='secret')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.context['strength'], {1:'weak', })

    def test_homepage_GET_strength_context_level_two(self):
        self.client.login(username='testuser', password='secret')

        self.playerscore.level = self.level2
        self.playerscore.save()

        response = self.client.get(reverse('home'))
        self.assertEqual(response.context['strength'], {1: 'weak', 2: 'strong',})


    def test_homepage_POST(self):
        self.client.login(username='testuser', password='secret')
        #As the level select buttons are actually icons the post form also contains where the
        #user selected the icon on the x and y axis.
        post_response = self.client.post('/', {'level_1.x': ['72'], 'level_1.y': ['79']})

        self.assertEqual(post_response.status_code, 302)
        self.assertEqual(post_response.url, 'courses/level_info/')

        #Test that playerstatus is created for user current level is set as level 1
        user = PlayerStatus.objects.filter(user = self.user).first()
        self.assertEqual(user.user, self.user)
        self.assertEqual(user.current_level, 1)

    def test_homepage_POST_under_threshold_level(self):
        self.client.login(username='testuser', password='secret')
        post_response = self.client.post('/', {'level_2.x': ['72'], 'level_2.y': ['79']})

        #Redirects to home
        self.assertEqual(post_response.status_code, 302)
        self.assertEqual(post_response.url, '/')

    def test_homepage_POST_over_threshold_level2(self):
        self.playerscore.level = self.level
        self.playerscore.current_level_score = 500
        self.playerscore.save()

        self.client.login(username='testuser', password='secret')
        response = self.client.get(reverse('home'))

        post_response = self.client.post('/', {'level_2.x': ['72'], 'level_2.y': ['79']})
        self.assertEqual(post_response.status_code, 302)
        self.assertEqual(post_response.url, 'courses/level_info/')

        user = PlayerStatus.objects.filter(user=self.user).first()
        self.assertEqual(user.current_level, 2)


    def test_activity_page_GET(self):
        self.client.login(username='testuser', password='secret')
        response = self.client.get(reverse('profile'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_activity_page_GET(self):
        self.client.login(username='testuser', password='secret')
        response = self.client.get(reverse('profile_month', args=[2020,2]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_scoreboard_page_GET(self):
        self.client.login(username='testuser', password='secret')
        response = self.client.get(reverse('scoreboard'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scoreboard.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_level_info_page_GET(self):
        s = self.client.session
        s.update({
            "results": ['test'],
            'level_up': False})
        s.save()
        self.client.login(username='testuser', password='secret')
        response = self.client.get(reverse('level_info'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'level_info.html')
    def test_level_info_load_data_GET(self):
        s = self.client.session
        s.update({
            "results": ['test'],
            'level_up': False})
        s.save()

        #Answered objects default for level is 1 if not provided.

        self.client.login(username='testuser', password='secret')
        response = self.client.get(reverse('level_info'))

        #Make sure makes questions from answered data
        question1 = Questions.objects.filter(spanish_id=self.answered.spanish_id).first()
        self.assertEqual(str(question1.spanish_id), str(self.answered.spanish_id))
        question_count = Questions.objects.all().count()
        self.assertEqual(question_count, 5)

        self.data = self.client.session['data']
        d = json.loads(self.data)

        # There should be 5 questions
        self.assertEqual(len(d), 5)



    def test_user_guide_page_GET(self):
        self.client.login(username='testuser', password='secret')
        response = self.client.get(reverse('instructions'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'instructions.html')













