from django.test import TestCase
from flashcard.views import UpdateItemsMixin
from django.contrib.auth import get_user_model
from courses.models import Levels, Spanish
from flashcard.models import Answered
from django.utils import timezone

class TestSMalgorithm(UpdateItemsMixin, TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
        username='testuser',
        email='test@email.com',
        password='secret'
        )
        self.level = Levels.objects.create(
            level_number = '2',
            points_threshold = '200',
            description = 'test'
        )
        self.spanish = Spanish.objects.create(
            spanish_phrase = 'me llamo',
            english_translation = 'my name is',
            level_number = self.level,
        )
        self.answered = Answered.objects.create(
            user = self.user,
            spanish_id = self.spanish,
            level_int = 2,
        )
        self.answered2 = Answered.objects.create(
            user=self.user,
            spanish_id=self.spanish,
            level_int=2,
            repetition = 1,
        )


    def test_review_time_1(self):
        self.quality = 5

        result = self.updateInterval(self.answered.ef, self.answered.repetition , self.quality)
        self.answered.ef = result[0]
        self.answered.repetition = result[1]

        setreview = self.setReview(self.answered.repetition)
        self.answered.quality_value = self.quality
        self.answered.review_time = setreview
        self.answered.last_review_day = timezone.now().date()
        self.assertEqual(self.answered.ef, 2.6)
        self.assertEqual(self.answered.repetition, 1)
        #remove seconds from review time
        self.reviewtime = self.answered.review_time.strftime("%Y-%m-%d, %H:%M")
        self.tomorrow = (timezone.now() + timezone.timedelta(hours=24)).strftime("%Y-%m-%d, %H:%M")
        self.assertEqual(self.reviewtime, self.tomorrow)

    def test_review_time_2(self):
        self.quality = 1

        result = self.updateInterval(self.answered.ef, self.answered.repetition, self.quality)
        self.answered.ef = result[0]
        self.answered.repetition = result[1]
        setreview = self.setReview(self.answered.repetition)
        self.answered.quality_value = self.quality
        self.answered.review_time = setreview
        self.answered.last_review_day = timezone.now().date()

        self.assertEqual(self.answered.ef, 2.5)
        self.assertEqual(self.answered.repetition, 1)
        # remove seconds from review time
        self.reviewtime = self.answered.review_time.strftime("%Y-%m-%d, %H:%M")
        self.tomorrow = (timezone.now() + timezone.timedelta(hours=24)).strftime("%Y-%m-%d, %H:%M")
        self.assertEqual(self.reviewtime, self.tomorrow)

    def test_review_time_3(self):
        self.quality = 5

        result = self.updateInterval(self.answered2.ef, self.answered2.repetition, self.quality)
        self.answered2.ef = result[0]
        self.answered2.repetition = result[1]

        setreview = self.setReview(self.answered2.repetition)
        self.answered2.quality_value = self.quality
        self.answered2.review_time = setreview
        self.answered2.last_review_day = timezone.now().date()
        self.assertEqual(self.answered2.ef, 2.6)
        self.assertEqual(self.answered2.repetition, 2)
        # remove seconds from review time
        self.reviewtime = self.answered2.review_time.strftime("%Y-%m-%d, %H:%M")
        self.due = (timezone.now() + timezone.timedelta(hours=48)).strftime("%Y-%m-%d, %H:%M")
        self.assertEqual(self.reviewtime, self.due)

    def test_review_time_4(self):
        self.quality = 5
        self.answered2.ef = 2.6
        self.answered2.save()

        result = self.updateInterval(self.answered2.ef, self.answered2.repetition, self.quality)
        self.answered2.ef = result[0]
        self.answered2.repetition = result[1]

        setreview = self.setReview(self.answered2.repetition)
        self.answered2.quality_value = self.quality
        self.answered2.review_time = setreview
        self.answered2.last_review_day = timezone.now().date()
        self.assertEqual(self.answered2.ef, 2.7)
        self.assertEqual(self.answered2.repetition, 2)
        # remove seconds from review time
        self.reviewtime = self.answered2.review_time.strftime("%Y-%m-%d, %H:%M")
        self.due= (timezone.now() + timezone.timedelta(hours=48)).strftime("%Y-%m-%d, %H:%M")
        self.assertEqual(self.reviewtime, self.due)

    def test_review_time_5(self):
        self.quality = 2

        result = self.updateInterval(self.answered2.ef, self.answered2.repetition, self.quality)
        self.answered2.ef = result[0]
        self.answered2.repetition = result[1]

        setreview = self.setReview(self.answered2.repetition)
        self.answered2.quality_value = self.quality
        self.answered2.review_time = setreview
        self.answered2.last_review_day = timezone.now().date()
        self.assertEqual(self.answered2.ef, 2.5)
        self.assertEqual(self.answered2.repetition, 1)
        # remove seconds from review time
        self.reviewtime = self.answered2.review_time.strftime("%Y-%m-%d, %H:%M")
        self.due = (timezone.now() + timezone.timedelta(hours=24)).strftime("%Y-%m-%d, %H:%M")
        self.assertEqual(self.reviewtime, self.due)


    def test_review_time_6(self):
        self.quality = 5
        self.answered2.ef = 2.5
        self.answered2.repetition = 2
        self.answered2.save()

        result = self.updateInterval(self.answered2.ef, self.answered2.repetition, self.quality)
        self.answered2.ef = result[0]
        self.answered2.repetition = result[1]

        setreview = self.setReview(self.answered2.repetition)
        self.answered2.quality_value = self.quality
        self.answered2.review_time = setreview
        self.answered2.last_review_day = timezone.now().date()
        self.assertEqual(self.answered2.ef, 2.6)
        self.assertEqual(self.answered2.repetition, 3)
        # remove seconds from review time
        self.reviewtime = self.answered2.review_time.strftime("%Y-%m-%d, %H:%M")
        self.due = (timezone.now() + timezone.timedelta(hours=72)).strftime("%Y-%m-%d, %H:%M")
        self.assertEqual(self.reviewtime, self.due)

    def test_review_time_7(self):
        self.quality = 5
        self.answered2.ef = 2.7
        self.answered2.repetition = 2
        self.answered2.save()

        result = self.updateInterval(self.answered2.ef, self.answered2.repetition, self.quality)
        self.answered2.ef = result[0]
        self.answered2.repetition = result[1]

        setreview = self.setReview(self.answered2.repetition)
        self.answered2.quality_value = self.quality
        self.answered2.review_time = setreview
        self.answered2.last_review_day = timezone.now().date()
        self.assertEqual(self.answered2.ef, 2.8)
        self.assertEqual(self.answered2.repetition, 3)
        # remove seconds from review time
        self.reviewtime = self.answered2.review_time.strftime("%Y-%m-%d, %H:%M")
        self.due = (timezone.now() + timezone.timedelta(hours=72)).strftime("%Y-%m-%d, %H:%M")
        self.assertEqual(self.reviewtime, self.due)

    def test_review_time_8(self):
        self.quality = 3
        self.answered2.ef = 2.5
        self.answered2.repetition = 2
        self.answered2.save()

        result = self.updateInterval(self.answered2.ef, self.answered2.repetition, self.quality)
        self.answered2.ef = result[0]
        self.answered2.repetition = result[1]

        setreview = self.setReview(self.answered2.repetition)
        self.answered2.quality_value = self.quality
        self.answered2.review_time = setreview
        self.answered2.last_review_day = timezone.now().date()
        self.assertEqual(self.answered2.ef, 2.4)
        self.assertEqual(self.answered2.repetition, 3)
        # remove seconds from review time
        self.reviewtime = self.answered2.review_time.strftime("%Y-%m-%d, %H:%M")
        self.due = (timezone.now() + timezone.timedelta(hours=72)).strftime("%Y-%m-%d, %H:%M")
        self.assertEqual(self.reviewtime, self.due)

    def test_review_time_9(self):
        self.quality = 2
        self.answered2.ef = 2.5
        self.answered2.repetition = 2
        self.answered2.save()

        result = self.updateInterval(self.answered2.ef, self.answered2.repetition, self.quality)
        self.answered2.ef = result[0]
        self.answered2.repetition = result[1]

        setreview = self.setReview(self.answered2.repetition)
        self.answered2.quality_value = self.quality
        self.answered2.review_time = setreview
        self.answered2.last_review_day = timezone.now().date()
        self.assertEqual(self.answered2.ef, 2.5)
        self.assertEqual(self.answered2.repetition, 1)
        # remove seconds from review time
        self.reviewtime = self.answered2.review_time.strftime("%Y-%m-%d, %H:%M")
        self.due = (timezone.now() + timezone.timedelta(hours=24)).strftime("%Y-%m-%d, %H:%M")
        self.assertEqual(self.reviewtime, self.due)

    def test_review_time_10(self):
        self.quality = 5
        self.answered2.ef = 2.8
        self.answered2.repetition = 3
        self.answered2.save()

        result = self.updateInterval(self.answered2.ef, self.answered2.repetition, self.quality)
        self.answered2.ef = result[0]
        self.answered2.repetition = result[1]

        setreview = self.setReview(self.answered2.repetition)
        self.answered2.quality_value = self.quality
        self.answered2.review_time = setreview
        self.answered2.last_review_day = timezone.now().date()
        self.assertEqual(self.answered2.ef, 2.9)
        self.assertEqual(self.answered2.repetition, 6)
        # remove seconds from review time
        self.reviewtime = self.answered2.review_time.strftime("%Y-%m-%d, %H:%M")
        self.due = (timezone.now() + timezone.timedelta(hours=144)).strftime("%Y-%m-%d, %H:%M")
        self.assertEqual(self.reviewtime, self.due)

    def test_review_time_11(self):
        self.quality = 3
        self.answered2.ef = 2.8
        self.answered2.repetition = 3
        self.answered2.save()

        result = self.updateInterval(self.answered2.ef, self.answered2.repetition, self.quality)
        self.answered2.ef = result[0]
        self.answered2.repetition = result[1]

        setreview = self.setReview(self.answered2.repetition)
        self.answered2.quality_value = self.quality
        self.answered2.review_time = setreview
        self.answered2.last_review_day = timezone.now().date()

        self.assertEqual(self.answered2.ef, 2.7)
        self.assertEqual(self.answered2.repetition, 5)
        # remove seconds from review time
        self.reviewtime = self.answered2.review_time.strftime("%Y-%m-%d, %H:%M")
        self.due = (timezone.now() + timezone.timedelta(hours=120)).strftime("%Y-%m-%d, %H:%M")
        self.assertEqual(self.reviewtime, self.due)

    def test_review_time_12(self):
        self.quality = 2
        self.answered2.ef = 2.8
        self.answered2.repetition = 3
        self.answered2.save()

        result = self.updateInterval(self.answered2.ef, self.answered2.repetition, self.quality)
        self.answered2.ef = result[0]
        self.answered2.repetition = result[1]

        setreview = self.setReview(self.answered2.repetition)
        self.answered2.quality_value = self.quality
        self.answered2.review_time = setreview
        self.answered2.last_review_day = timezone.now().date()

        self.assertEqual(self.answered2.ef, 2.8)
        self.assertEqual(self.answered2.repetition, 1)
        # remove seconds from review time
        self.reviewtime = self.answered2.review_time.strftime("%Y-%m-%d, %H:%M")
        self.due = (timezone.now() + timezone.timedelta(hours=24)).strftime("%Y-%m-%d, %H:%M")
        self.assertEqual(self.reviewtime, self.due)

    def test_review_time_13(self):
        self.quality = 5
        self.answered2.ef = 2.9
        self.answered2.repetition = 4
        self.answered2.save()

        result = self.updateInterval(self.answered2.ef, self.answered2.repetition, self.quality)
        self.answered2.ef = result[0]
        self.answered2.repetition = result[1]

        setreview = self.setReview(self.answered2.repetition)
        self.answered2.quality_value = self.quality
        self.answered2.review_time = setreview
        self.answered2.last_review_day = timezone.now().date()

        self.assertEqual(self.answered2.ef, 3.0)
        self.assertEqual(self.answered2.repetition, 9)
        # remove seconds from review time
        self.reviewtime = self.answered2.review_time.strftime("%Y-%m-%d, %H:%M")
        self.due = (timezone.now() + timezone.timedelta(hours=216)).strftime("%Y-%m-%d, %H:%M")
        self.assertEqual(self.reviewtime, self.due)






