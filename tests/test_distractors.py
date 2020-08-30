from django.test import TestCase
from django.contrib.auth import get_user_model
from courses.models import Levels, UserSessions, Spanish, PlayerStatus, PlayerScore
from construct.models import Verbs, Pronouns
from django.urls import reverse
from flashcard.models import Answered, Questions
import json
import datetime
from courses.views import LoadQuestionsMixin, InitializeMixin
from django.utils import timezone

class TestFlashcardDistractors(TestCase, LoadQuestionsMixin):
    def setUp(self):
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
            level_number=self.level2,
            type = 'verb',
        )
        self.spanish2 = Spanish.objects.create(
            spanish_phrase='tester',
            english_translation='test2',
            level_number=self.level2,
            type ='pronoun',)


        self.spanish3 = Spanish.objects.create(
            spanish_phrase='tested',
            english_translation='test3',
            level_number=self.level2,
            type = 'verb'
        )

        self.spanish4 = Spanish.objects.create(
            spanish_phrase='test',
            english_translation='test',
            level_number=self.level2,
            type = 'verb')

        self.spanish5 = Spanish.objects.create(
            spanish_phrase='west',
            english_translation='west',
            level_number=self.level2,
            type = 'verb')

        #This object is level 1 and not a verb
        self.spanish6 = Spanish.objects.create(
            spanish_phrase = 'testy',
            english_translation = 'testy',
            level_number = self.level,
            type= 'noun',)

    def test_same_type_chosen_flashcard_distractors(self):
        distractors = self.load_distractors2(self.spanish3)
        expected_distractors = ['testing','test','west']
        self.assertEqual(distractors, expected_distractors)

    def test_same_type_different_level_flashcard_distractors(self):
        #Change so level 1 object is same type and a level 2 same type object becomes not the same type.
        #Expect that list should change and level 1 object is chosen in place.
        self.spanish6.type = 'verb'
        self.spanish6.save()
        self.spanish5.type = 'noun'
        self.spanish5.save()

        distractors = self.load_distractors2(self.spanish3)
        expected_distractors = ['test','testing', 'testy']
        self.assertEqual(distractors, expected_distractors)

class TestConstructDistractors(TestCase, LoadQuestionsMixin):
    def setUp(self):
        self.level = Levels.objects.create(
            level_number='1',
            points_threshold='100',
            description='test'
        )
        self.spanish1 = Spanish.objects.create(
            spanish_phrase = 'te llamas',
            english_translation = 'your name',
            level_number = self.level,
            type = 'phrase')

        self.verb = Verbs.objects.create(
            infinitive = 'llamar',
            yo = 'llamo',
            tú = 'llamas',
            usted_él_ella = 'llama',
            nosotros_nosotras = 'llamamos',
            vosotros_vosotras = 'llamáis',
            ustedes_ellos_ellas = 'llaman',
        )
        self.pronoun1 = Pronouns.objects.create(
            spanish = 'te',
            person = 'you',
            pronoun_type = 'reflexive',

        )
        self.pronoun2 = Pronouns.objects.create(
            spanish='me',
            person='I',
            pronoun_type='reflexive',
        )

    def test_construct_distractors(self):
        distractors = self.load_construct_distractors(self.spanish1)

        self.assertEqual(len(distractors), 2)
        #cannot test exact list as randomly selected