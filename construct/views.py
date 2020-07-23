from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.context_processors import request
from django.views.generic import CreateView, ListView, DetailView, FormView
from django.views import View
import json
from courses.models import Spanish, PlayerScore, PlayerStatus, Levels, UserSessions
from courses.views import InitializeMixin, LoadQuestionsMixin
from flashcard.views import UpdateItemsMixin
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
from .models import Verbs
from datetime import date
# Create your views here.

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
        print(matrix)
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


class ConstructGame(LoginRequiredMixin, UpdateItemsMixin, LoadQuestionsMixin, InitializeMixin, CompareMixin, View):
    template_name = 'construct.html'

    def get(self, request):

        # If session level hasn't been given a value this means the session hasn't been initialized
        # For example if user has gone straigt to level info url without selecting a level previously

        initialized, created = PlayerStatus.objects.get_or_create(user=self.request.user)

        if initialized.current_level == 0:
            level = self.initializeQuiz(request)
            answered_data = self.load_data(level, self.request.user)
            print('YESSSSS')
            print('answered data', answered_data)
            self.get_questions2(answered_data, level, request)
            print('had not been intialized')
        if 'data' not in request.session:
            level = self.initializeQuiz(request)
            answered_data = self.load_data(level, self.request.user)
            self.get_questions2(answered_data, level, request)


        data = request.session['data']
        d = json.loads(data)


        # Get current question from user status
        status = PlayerStatus.objects.filter(user=self.request.user).first()
        question_num = int(status.currentQuestion)
        lives = 3 - status.currentErrors

        # remainder of (question number, total number of questions)-  Serve the (remainder)th question for the level
        # This is for when there are less than 10 questions
        n = int(question_num) % int(len(d))
        data = d[n]


        english = Spanish.objects.filter(spanish_phrase=data['fields']['spanish_id']).values(
            'english_translation').first()

        spanish = data['fields']['spanish_id']
        #This makes a list of spanish split into elements in order to decide if it should be split by character of word
        spanishwords = spanish.split()
        #if len(spanishwords) > 2 and question_num % 3 != 1:
        if len(spanishwords) > 2:
            if '?' in spanish:
                spanishwords = spanish[1:-1].split()
                spanishwords = spanishwords + ['?', '¿']
            words = set(spanishwords)
            p = sample(words, (len(words)))
            sentence = True

        # buttons for letters
        else:
            characters = set(spanish)
            p = sample(characters, (len(characters)))
            print('word length',len(p))
            sentence = False



        context = {
            'question': english['english_translation'],
            'spanish': spanish,
            'spanish_words': spanishwords,
            'characters': p,
            'question_num': question_num + 1,
            'number':data['pk'],
            'word_length': len(p),
            'sentence': sentence,
            'level': data['fields']['level'],
            'lives':lives,

                   }
        return render(request, self.template_name, context)



    def post(self,request):
        answer = request.POST['user_input']
        #remove double spacing if exists


        # Need to check for extra spacing between words also
        answer = re.sub(' +', ' ', answer)


        question_id = int(request.POST['question-id'])
        question_num = int(request.POST['question-num'])-1
        sentence = request.POST.get('sentence',False)
        level = int(request.POST['level'])

        # Get JSON data for question number
        data = request.session['data']
        d = json.loads(data)

        # remainder of (question number, total number of questions)-  Serve the (remainder)th question for the level
        # This is for when there are less than 10 questions
        n = int(question_num) % int(len(d))
        data = d[n]

        # Get correct answer from JSON data
        correct_answer = data['fields']['correct_answer']

        status, created = PlayerStatus.objects.get_or_create(user=self.request.user)
        status.currentQuestion = int(question_num + 1)
        status.save()

        correct_answer2 = correct_answer
        #Remove punctuation from correct answer if missing from answer
        if correct_answer.startswith('¿' or '¡'):
            if not answer.startswith('¿' or '¡'):
                correct_answer2 = correct_answer[1:-1]


        answer = answer.lower()
        correct_answer2 = correct_answer2.lower()

        if correct_answer2 == answer:
            status, created = PlayerStatus.objects.get_or_create(user=self.request.user)
            status.currentScore = int(status.currentScore) + 1
            status.save()
            messages.success(request, "Yohoo! Correct answer, keep up the streak :)")
        else:
            status.currentErrors += 1
            status.save()
            messages.error(request, "Bummer! Wrong answer, try again :(")

        quality = self.findQuality(answer, correct_answer, sentence)



        #Save quality of answer in results session data
        saved_results = request.session['results']
        if correct_answer not in saved_results:
            saved_results[correct_answer] = (quality,)
        else:
            results = saved_results[correct_answer]
            results.append(quality)
            saved_results[correct_answer] = results
        request.session['results'] = saved_results

        #update Answered model with quality response
        spanishObj = Spanish.objects.get(spanish_phrase=correct_answer)
        answered, created = Answered.objects.get_or_create(user=self.request.user,
                                                           spanish_id=spanishObj,
                                                           level_int = spanishObj.level_number.level_number)
        # Firstly update the repetition number for the phrase for the user and the quality
        answered.quality_value = quality


        result = self.updateInterval(answered.ef, answered.repetition, quality)
        answered.ef = result[0]
        answered.repetition = result[1]

        review = self.setReview(answered.repetition)
        answered.review_time = review
        answered.quality_value = quality
        answered.last_review_day = timezone.now().date()
        answered.save()



        if status.currentErrors >= 3:
            return redirect('/game_over/')

        if status.currentQuestion == 10:
            request.session['initialized'] = False
            return redirect('/construct/construct_result/')


        return redirect('construct')




class ConstructResult(LoginRequiredMixin, View):
    template_name = 'construct_result.html'

    def get(self,request):
        status, created = PlayerStatus.objects.get_or_create(user=self.request.user)
        game_score = int(status.currentScore)

        # Add session to user session
        session, created = UserSessions.objects.get_or_create(user=self.request.user,
                                                              session=datetime.datetime.now().date())

        user = PlayerScore.objects.get(user=self.request.user)
        user.score = int(user.score) + game_score

        # Add game points to current level points only if the game was played in the user's top level
        if int(status.current_level) == int(user.level.level_number):
            user.current_level_score = user.current_level_score + game_score

        # If points threshold is met for level user can level up
        level_detail = Levels.objects.filter(level_number=str(user.level)).first()
        print('level detail', level_detail)
        if user.current_level_score >= level_detail.points_threshold:
            # level up
            # Get next level model
            levelUp = str(user.level.level_number + 1)
            levelUp_detail = Levels.objects.get(level_number=levelUp)
            user.level = levelUp_detail
            user.current_level_score = 0
            request.session['level_up'] = True

        # get data results

        saved_results = request.session['results']


        # Reset current user details to 0
        status.currentQuestion = 0
        status.current_level = 0
        status.currentScore = 0
        status.save()
        user.save()
        request.session['data'] = ""

        context = {
            'score': game_score,
            'data': saved_results,
            'level_up': request.session['level_up'],


            }

        return render(request, self.template_name, context)


