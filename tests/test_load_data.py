from django.test import TestCase
from courses.views import LoadQuestionsMixin
from django.contrib.auth import get_user_model
from courses.models import Levels, UserSessions,Spanish
from flashcard.models import Answered
import datetime
from django.utils import timezone

class LoadTest(TestCase, LoadQuestionsMixin):
    def setUp(self):
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

        self.userSession = UserSessions.objects.create(
            user=self.user,
            session=datetime.datetime.now().date(),
        )

        #Zero rep items
        self.spanish1 = Spanish.objects.create(
                            spanish_phrase= 'me llamo',
                            english_translation = 'your name is',
                            level_number = self.level)
        self.spanish2 = Spanish.objects.create(
                            spanish_phrase= 'te llamas',
                            english_translation = 'your name is',
                            level_number = self.level)
        self.answered1 = Answered.objects.create(user=self.user, spanish_id=self.spanish1)
        self.answered2 = Answered.objects.create(user=self.user, spanish_id=self.spanish2)

        #due item
        self.spanish3 = Spanish.objects.create(
            spanish_phrase='estas listos',
            english_translation='are you ready',
            level_number=self.level)
        self.spanish4 = Spanish.objects.create(
            spanish_phrase='cuando',
            english_translation='when',
            level_number=self.level)

        self.answered3 = Answered.objects.create(user=self.user, spanish_id=self.spanish3, repetition =2, review_time = timezone.now())
        self.answered4 = Answered.objects.create(user=self.user, spanish_id=self.spanish4, repetition=1, review_time = timezone.now(),)

        #quality less than 4 reviewed today
        self.spanish5 = Spanish.objects.create(
            spanish_phrase='estoy enfadado',
            english_translation="I'm angry",
            level_number=self.level)
        self.spanish6 = Spanish.objects.create(
            spanish_phrase='el supermercado',
            english_translation='the supermarket',
            level_number=self.level)
        self.answered5 = Answered.objects.create(user=self.user, spanish_id=self.spanish5,
                     quality_value = 3, repetition = 1, last_review_day = timezone.now(),
                     review_time = (timezone.now() + timezone.timedelta(hours=48)))
        self.answered6 = Answered.objects.create(user=self.user, spanish_id=self.spanish6,
                     quality_value = 3, repetition = 1, last_review_day = timezone.now(),
                     review_time = (timezone.now() + timezone.timedelta(hours=48)))

        #ranked
        self.spanish7 = Spanish.objects.create(
            spanish_phrase='donde vives',
            english_translation="where do you live",
            level_number=self.level)
        self.spanish8 = Spanish.objects.create(
            spanish_phrase='Inglaterra',
            english_translation='England',
            level_number=self.level)
        self.spanish9 = Spanish.objects.create(
            spanish_phrase='en Espana',
            english_translation="in Spain",
            level_number=self.level)
        self.spanish10 = Spanish.objects.create(
            spanish_phrase='yo vivo en estas puebla',
            english_translation='I live in this town',
            level_number=self.level)
        self.answered7 = Answered.objects.create(user = self.user, spanish_id = self.spanish7, quality_value =5, repetition = 1,
                     review_time = timezone.now() + timezone.timedelta(hours =20))
        self.answered8 = Answered.objects.create(user=self.user, spanish_id=self.spanish8, quality_value=5, repetition=1,
                     review_time=timezone.now() + timezone.timedelta(hours=24))
        self.answered9 = Answered.objects.create(user=self.user, spanish_id=self.spanish9, quality_value=5, repetition=1,
                     review_time=timezone.now() + timezone.timedelta(hours=30))
        self.answered10 = Answered.objects.create(user=self.user, spanish_id=self.spanish10, quality_value=5, repetition=1,
                     review_time=timezone.now() + timezone.timedelta(hours=100))


    def test_load_data(self):
        answered_data = self.load_data([1,], self.user)
        expected_data = [self.answered1.spanish_id, self.answered2.spanish_id,
                         self.answered3.spanish_id, self.answered4.spanish_id,
                         self.answered5.spanish_id, self.answered6.spanish_id,
                         self.answered7.spanish_id, self.answered8.spanish_id,
                         self.answered9.spanish_id, self.answered10.spanish_id, ]
        print(answered_data)
        self.assertEqual(answered_data,expected_data)

    def test_load_data2(self):
        #add a ranked item to quality less than 4 reviewed today and another reviewed yesterday
        self.answered10.quality_value = 3
        #self.answered10 should then be prioritised before self.answered7 (review date today automatic)
        self.answered10.save()
        self.answered9.quality_value = 3
        self.answered9.last_review_day = timezone.now() - timezone.timedelta(hours=24)
        self.answered9.save()
        #self.answered 9 shouldn't move and be ranked last
        answered_data = self.load_data([1,], self.user)
        expected_data = [self.answered1.spanish_id, self.answered2.spanish_id,
                         self.answered3.spanish_id, self.answered4.spanish_id,
                         self.answered5.spanish_id, self.answered6.spanish_id,
                         self.answered10.spanish_id, self.answered7.spanish_id,
                         self.answered8.spanish_id, self.answered9.spanish_id, ]
        self.assertEqual(answered_data, expected_data)

    def test_load_data3(self):
        #Reduce answered.10 review time so that it is ranked first
        self.answered10.review_time = timezone.now() + timezone.timedelta(hours=10)
        self.answered10.save()
        answered_data = self.load_data([1,], self.user)
        expected_data = [self.answered1.spanish_id, self.answered2.spanish_id,
                         self.answered3.spanish_id, self.answered4.spanish_id,
                         self.answered5.spanish_id, self.answered6.spanish_id,
                         self.answered10.spanish_id, self.answered7.spanish_id,
                         self.answered8.spanish_id, self.answered9.spanish_id,]
        self.assertEqual(answered_data, expected_data)

    def test_load_data4(self):
        #self.answered1 rep will be changed to 1 but as review time is default set to today, it will be due
        self.answered1.repetition = 1
        self.answered1.save()
        answered_data = self.load_data([1,], self.user)
        expected_data = [self.answered2.spanish_id, self.answered1.spanish_id,
                         self.answered3.spanish_id, self.answered4.spanish_id,
                         self.answered5.spanish_id, self.answered6.spanish_id,
                         self.answered7.spanish_id, self.answered8.spanish_id,
                         self.answered9.spanish_id, self.answered10.spanish_id, ]
        self.assertEqual(answered_data, expected_data)

    def test_overdue(self):
        self.answered10.review_time = timezone.now() - timezone.timedelta(hours=24)
        #answered10 should be ranked as overdue and prioritized third (just after first two that are on zero rep).
        self.answered10.save()
        answered_data = self.load_data([1,], self.user)
        expected_data = [self.answered1.spanish_id, self.answered2.spanish_id,
                         self.answered10.spanish_id, self.answered3.spanish_id,
                         self.answered4.spanish_id, self.answered5.spanish_id,
                         self.answered6.spanish_id, self.answered7.spanish_id,
                         self.answered8.spanish_id, self.answered9.spanish_id,]
        self.assertEqual(answered_data, expected_data)

        #BUT ALL DUE OR OVERDUE ITEMS ARE TREATED THE SAME
        #answered 10 is actually overdue a day, whereas answered 3 and 4 are due today.

    def test_prioirty_overdue_items(self):
        #Update answered 4 to be more overdue that answered 3 and objects will switch places in list
        self.answered4.review_time = timezone.now() - timezone.timedelta(hours=24)
        self.answered4.save()
        answered_data = self.load_data([1, ], self.user)
        expected_data = [self.answered1.spanish_id, self.answered2.spanish_id,
                         self.answered4.spanish_id, self.answered3.spanish_id,
                         self.answered5.spanish_id, self.answered6.spanish_id,
                         self.answered7.spanish_id, self.answered8.spanish_id,
                         self.answered9.spanish_id, self.answered10.spanish_id, ]
        self.assertEqual(answered_data, expected_data)

