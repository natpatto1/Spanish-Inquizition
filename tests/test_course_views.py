from django.test import TestCase
from django.contrib.auth import get_user_model
from courses.models import Levels, UserSessions, Spanish, PlayerStatus, PlayerScore
from django.urls import reverse
from flashcard.models import Answered
import json
import datetime
from courses.views import LoadQuestionsMixin, InitializeMixin



class TestViews(TestCase):
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

        self.userSession = UserSessions.objects.create(
            user = self.user,
            session = datetime.datetime.now().date(),
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

        self.playerscore = PlayerScore.objects.create(
            user = self.user,
            level = self.level,
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


    def test_homepage_GET_level_up(self):
        self.playerscore.score = 150
        self.playerscore.save()

        self.client.login(username='testuser', password='secret')
        response = self.client.get(reverse('home'))

        self.playerscore.refresh_from_db()

        self.assertEqual(str(self.playerscore.level), str(self.level2))


    def test_homepage_POST(self):
        self.client.login(username='testuser', password='secret')
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
        self.playerscore.score = 150
        self.playerscore.save()

        self.client.login(username='testuser', password='secret')
        response = self.client.get(reverse('home'))

        post_response = self.client.post('/', {'level_2.x': ['72'], 'level_2.y': ['79']})
        self.assertEqual(post_response.status_code, 302)
        self.assertEqual(post_response.url, 'courses/level_info/')

        user = PlayerStatus.objects.filter(user=self.user).first()
        self.assertEqual(user.current_level, 2)

    def test_homepage_POST_question_data(self):
        self.answered = Answered.objects.create(
            user = self.user,
            spanish_id = self.spanish
        )
        self.answered2 = Answered.objects.create(
            user=self.user,
            spanish_id=self.spanish2
        )
        self.answered3 = Answered.objects.create(
            user=self.user,
            spanish_id=self.spanish3
        )
        self.answered4 = Answered.objects.create(
            user=self.user,
            spanish_id=self.spanish4
        )
        self.answered5 = Answered.objects.create(
            user=self.user,
            spanish_id=self.spanish5
        )

        self.client.login(username='testuser', password='secret')
        post_response = self.client.post('/', {'level_1.x': ['72'], 'level_1.y': ['79']})

        self.data = self.client.session['data']
        d = json.loads(self.data)

        #There should be 5 questions
        self.assertEqual(len(d), 5)


    def test_profile_page_GET(self):
        self.client.login(username='testuser', password='secret')
        response = self.client.get(reverse('profile'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_profile_month_page_GET(self):
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













