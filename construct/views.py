from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.context_processors import request
from django.views.generic import CreateView, ListView, DetailView, FormView
from django.views import View
import json
from courses.models import Spanish, PlayerScore, PlayerStatus, Levels, UserSessions
from courses.views import InitializeMixin, LoadQuestionsMixin
from flashcard.views import UpdateItemsMixin, Game
from random import sample
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
import numpy as np
from flashcard.models import Answered
from datetime import timedelta
from django.utils import timezone
import datetime
import re

from django.contrib.postgres.search import SearchVector




class CompareMixin(object):
    def findQuality(self, answer, correct_answer, sentence):
        answer = answer.lower()
        correct_answer = correct_answer.lower()
        if answer == '':
            quality = 0
        else:
            quality = self.dumbDiff(answer, correct_answer)
            if quality == 1:
                    quality = self.levenshtein(answer, correct_answer,sentence)
        return quality

    def dumbDiff(self, answer, correct_answer):
        if answer == correct_answer:
            return 5
        else:
            return 1

    def levenshtein(self, answer, correct_answer, sentence):
        # If punctuation is missing at start and end count as only one mistake
        if correct_answer.startswith('¿' or '¡'):
            if not answer.startswith('¿' or '¡'):
                correct_answer = correct_answer[1:-1]
        if sentence == True:
            answer = answer.split()
            correct_answer = correct_answer.split()

        size_x = len(answer) + 1
        size_y = len(correct_answer) + 1
        matrix = np.zeros((size_x, size_y))
        for x in range(size_x):
            matrix[x, 0] = x
        for y in range(size_y):
            matrix[0, y] = y

        for x in range(1, size_x):
            for y in range(1, size_y):
                if answer[x - 1] == correct_answer[y - 1]:
                    matrix[x, y] = min(
                        matrix[x - 1, y] + 1,
                        matrix[x - 1, y - 1],
                        matrix[x, y - 1] + 1
                    )
                else:
                    matrix[x, y] = min(
                        matrix[x - 1, y] + 1,
                        matrix[x - 1, y - 1] + 1,
                        matrix[x, y - 1] + 1
                    )

        if (matrix[size_x - 1, size_y - 1]) == 0:
            return 5
        if (matrix[size_x - 1, size_y - 1]) == 1:  # one edit needed
            return 4
        if (matrix[size_x - 1, size_y - 1]) == 2:  # two edits needed
            return 3
        if (matrix[size_x - 1, size_y - 1]) == 3:
            return 2
        if (matrix[size_x - 1, size_y - 1]) > 3:
            return 1


class ConstructGame(Game, CompareMixin):
    template_name = 'construct.html'

    def make_option_buttons(self,request):
        # This makes a list of spanish split into elements in order to decide if it should be split by character of word
        self.spanishwords = self.spanish.split()
        # if len(spanishwords) > 2 and question_num % 3 != 1:
        if len(self.spanishwords) > 1:
            if '?' in self.spanish:
                self.spanishwords = self.spanish[1:-1].split()
                self.spanishwords = self.spanishwords + ['?', '¿']
            words = list(self.spanishwords)
            
            # Get phrase distractors if exist
            if self.data['fields']['construct_one'] != '':
                words.append(self.data['fields']['construct_one'])
                if self.data['fields']['construct_two'] != '':
                    words.append(self.data['fields']['construct_two'])
                    if words.append(self.data['fields']['construct_three']) != '':
                        words.append(self.data['fields']['construct_three'])
            self.p = sample(words, (len(words)))
            self.sentence = True

        # buttons for letters
        else:
            characters = list(self.spanish)
            self.p = sample(characters, (len(characters)))

            self.sentence = False


    def get(self, request):

        self.get_quiz_data(request, 'construct')

        self.data = self.get_current_question(request)


        self.make_option_buttons(request)




        context = {
            'question': self.english['english_translation'],
            'spanish': self.spanish,
            'spanish_words': self.spanishwords,
            'characters': self.p,
            'question_num': self.question_num + 1,
            'number':self.data['pk'],
            'word_length': len(self.p),
            'sentence': self.sentence,
            'level': self.data['fields']['level'],
            'lives': 3 - self.status.currentErrors,
            'review': False

                   }
        return render(request, self.template_name, context)

    def format_answer_and_target_before_comparing(self, request):

        self.correct_answer2 = self.correct_answer
        self.correct_answer2 = self.correct_answer2.replace(u"\u00A0", " ")
        # Remove punctuation from correct answer if missing from answer
        if self.correct_answer.startswith('¿') or self.correct_answer.startswith('¡'):
            if not self.answer.startswith('¿') or self.answer.startswith('¡'):
                self.correct_answer2 = self.correct_answer[1:-1]

        self.answer = self.answer.lower()
        self.correct_answer2 = self.correct_answer2.lower()

    def check_answer(self, request, quality):
        print(self.answer, 'answer')
        print(self.correct_answer2, 'correct')
        if self.correct_answer2 == self.answer:
            status, created = PlayerStatus.objects.get_or_create(user=self.request.user)
            status.currentScore = int(status.currentScore) + 2
            status.save()
            messages.success(request, "Yohoo! Correct answer, keep up the streak :)")
        elif quality == 4:
            self.status.currentScore = int(self.status.currentScore) + 1
            self.status.save()
            messages.error(request, "Almost there! Try again :(")
        else:
            self.status.currentErrors += 1
            self.status.save()
            messages.error(request, "Bummer! Wrong answer, try again :(")


    def post(self,request):

        self.get_and_format_POST_data(request)


        self.correct_answer = self.get_POST_correct_answer(request)



        self.POST_increment_current_question(request)
        self.format_answer_and_target_before_comparing(request)



        self.quality = self.findQuality(self.answer, self.correct_answer2, self.sentence)

        self.check_answer(request,self.quality)


        self.answered = self.POST_update_Answered_data(request)
        self.POST_save_to_results(request)



        self.POST_check_end_game_conditions(request)


        if self.status.currentQuestion == 10:
            system_messages = messages.get_messages(request)
            for message in system_messages:
                pass
            system_messages.used = True
            request.session['initialized'] = False
            return redirect('result')


        return redirect('construct')

