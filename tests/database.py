from django.conf import settings
from django.db import connection
from django.test import TestCase
from django.contrib.auth import get_user_model

from courses.models import Spanish, PlayerStatus, Levels
from flashcard.models import Answered

class TestDatabaseQueries(TestCase):

    def setUp(self):
        # self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@email.com',
            password='secret'
        )
        self.playerstatus = PlayerStatus.objects.create(
            user=self.user,
            current_level='1',

        )
        self.level = Levels.objects.create(
            level_number='1',
            points_threshold='100',
            description='test'
        )
        self.spanish = Spanish.objects.create(
            spanish_phrase='testing',
            english_translation='test',
            level_number=self.level
        )


    def test_answered_test(self):
        get_response = self.client.get('/users/login/')
        post_response = self.client.post('/users/login/', {'username': 'testuser', 'password': 'secret'})
        settings.DEBUG = True

        level = PlayerStatus.objects.filter(user=self.user).first()
        current_level = int(level.current_level)
        spanish_list = Spanish.objects.filter(level_number=current_level)
        level_desc = Levels.objects.filter(level_number=current_level).first()
        level_desc = level_desc.description

        # Need to create answered objects if not already existing for user and level
        for item in spanish_list:

            spanish = Spanish.objects.get(spanish_phrase=item)
            answered, created = Answered.objects.get_or_create(user=self.user,
                                                               spanish_id=spanish,
                                                               level_int=spanish.level_number.level_number)
            answered.save()

        self.assert_(connection.queries, '2 queries')
        print(connection.queries)


        settings.DEBUG = False