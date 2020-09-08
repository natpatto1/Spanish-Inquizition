from django.test import TestCase
from construct.models import Verbs
from construct.views import CompareMixin


class TestLevenshchtein(TestCase, CompareMixin):
    def test_1_edit(self):
        answer = 'te llama'
        correct_answer = 'te llamas'
        sentence = False
        quality = self.findQuality(answer, correct_answer, sentence)
        #Would take 1 edit to change string te llama to te llamas - therefore quality 4
        self.assertEqual(quality, 4)

    def test_no_edits(self):
        answer = 'te llamas'
        correct_answer = 'te llamas'
        sentence = False
        quality = self.findQuality(answer, correct_answer, sentence)
        self.assertEqual(quality, 5)


    def test_punctuation_missing(self):
        answer = 'Cómo se Dice'
        correct_answer = '¿Cómo Se Dice?'
        sentence = True
        quality = self.findQuality(answer, correct_answer, sentence)
        #as only punctuation missing, this would be 5 quality
        self.assertEqual(quality,5)


    def test_sentence_2_edits(self):
        answer = 'puedo no comer'
        correct_answer = 'no puedo comer'
        sentence = True
        quality = self.findQuality(answer, correct_answer, sentence)
        #Two edits needed therefore quality 3 is returned
        self.assertEqual(quality,3)

    def test_4_edits(self):
        answer = 'donde'
        correct_answer = 'donde vas'
        sentence = False
        quality = self.findQuality(answer, correct_answer, sentence)
        self.assertEqual(quality, 1)

    def test_3_edits(self):
        answer = 'Espanyia'
        correct_answer = 'España'
        sentence = False
        quality = self.findQuality(answer, correct_answer, sentence)
        #3 edits needed so quality should be 2
        self.assertEqual(quality,2)