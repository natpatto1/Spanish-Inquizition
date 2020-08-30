from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from courses.models import Levels, Spanish, PlayerScore,PlayerStatus, UserSessions
from courses.views import InitializeMixin, LoadQuestionsMixin
from django.views.generic import CreateView, ListView, DetailView, FormView
from django.db import connection
import random
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.views import View
from .models import Answered, Questions
from random import shuffle
from django.shortcuts import redirect
from django.contrib import messages
import json
from datetime import timedelta
from django.utils import timezone
import datetime
from datetime import date
from django.core import serializers
from django.utils.timezone import make_aware
import re

import difflib

# Create your views here.

class UpdateItemsMixin(object):

    def updateInterval(self, currentEF, repetition, quality):

        if quality >= 3:
            EF = currentEF + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
            EF = round(EF, 1)
            # If EF is less than 1.3 then let EF be 1.3
            if EF < 1.3:
                EF = 1.3

            if repetition <= 2:
                repetition = repetition + 1

            # Calculate new repetition interval
            # needs updating based on whether it has been seen more than twice.
            else:
                repetition = (repetition - 1) * EF

                # if interval is a fraction, round it to the nearest integer
                repetition = round(repetition, 0)

                # set limit of interval 9 (180 days)
                if repetition > 180:
                    repetition = 180


        else:
            repetition = 1
            EF = currentEF

        return (EF, repetition)

    def setReview(self, repetition):
        # Updates review time
        intervalHours = 24 * repetition
        reviewTime = timezone.now() + timezone.timedelta(hours=intervalHours)
        return reviewTime

class Game(LoginRequiredMixin,LoadQuestionsMixin,InitializeMixin,UpdateItemsMixin, View):
    def get_quiz_data(self, request,game):
        # If session level hasn't been given a value this means the session hasn't been initialized
        # For example if user has gone straigt to flashcard url without selecting a level previously

        self.status, created = PlayerStatus.objects.get_or_create(user=self.request.user)
        if self.status.current_level == 0:
            self.status.current_level = self.initializeQuiz(request)
            level = [self.initializeQuiz(request), ]
            answered_data = self.load_data(level, self.request.user)
            self.get_questions2(answered_data, request)
        self.status.review_game = False
        self.status.game = game
        self.status.save()

        if 'data' not in request.session:
            level = [self.initializeQuiz(request), ]
            answered_data = self.load_data(level, self.request.user)
            self.get_questions2(answered_data, request)

    def get_current_question(self, request):

        data = request.session['data']
        self.d = json.loads(data)

        # Get current question from user status
        #self.status = PlayerStatus.objects.filter(user=self.request.user).first()
        self.question_num = int(self.status.currentQuestion)

        try:
            n = int(self.question_num) % int(len(self.d))
            data = self.d[n]
        except:
            level = [self.initializeQuiz(request),]
            answered_data = self.load_data(level, self.request.user)
            self.get_questions2(answered_data, request)
            data = request.session['data']
            d = json.loads(data)
            n = int(self.question_num) % int(len(d))
            data = d[n]
        self.english = Spanish.objects.filter(spanish_phrase=data['fields']['spanish_id']).values(
            'english_translation').first()
        self.spanish = data['fields']['spanish_id']
        return data

    def get_and_format_POST_data(self, request):

        self.question_id = int(request.POST['question-id'])
        answer = str(request.POST['answer'])
        answer = re.sub(' +', ' ', answer)
        answer = re.sub('&nbsp;', ' ', answer)
        self.answer = answer.replace(u"\u00A0", " ")
        try:
            self.sentence = request.POST.get('sentence', False)
        finally:

            self.question_num = int(request.POST['question-num']) - 1
            self.level = int(request.POST['level'])



    def get_POST_correct_answer(self, request):

        # Get JSON data for question number
        data = request.session['data']
        d = json.loads(data)

        # remainder of (question number, total number of questions)-  Serve the (remainder)th question for the level
        # This is for when there are less than 10 questions
        n = int(self.question_num) % int(len(d))
        data = d[n]

        # Get correct answer from JSON data
        correct_answer = str(data['fields']['correct_answer'])

        return correct_answer

    def POST_increment_current_question(self, request):

        self.status, created = PlayerStatus.objects.get_or_create(user=self.request.user)
        self.status.currentQuestion = int(self.question_num + 1)
        self.status.save()

    def POST_update_Answered_data(self, request):
        spanishObj = Spanish.objects.get(spanish_phrase=self.correct_answer)

        self.answered, created = Answered.objects.get_or_create(user=self.request.user,
                                                           spanish_id=spanishObj,
                                                           level_int=spanishObj.level_number.level_number)

        result = self.updateInterval(self.answered.ef, self.answered.repetition, self.quality)
        self.answered.ef = result[0]
        self.answered.repetition = result[1]

        ##If repetition is less than or more than 2 call setReview function also needs to be called
        setreview = self.setReview(self.answered.repetition)
        self.answered.quality_value = self.quality
        self.answered.review_time = setreview
        self.answered.last_review_day = timezone.now().date()

        self.answered.save()

        return self.answered

    def POST_save_to_results(self, request):

        saved_results = request.session['results']
        if self.correct_answer not in saved_results:
            saved_results[self.correct_answer] = (self.quality,)
        else:

            results = saved_results[self.correct_answer]
            results.append(self.quality)
            saved_results[self.correct_answer] = results
        request.session['results'] = saved_results


    def POST_check_end_game_conditions(self, request):

        if self.status.currentErrors >= 3:
            system_messages = messages.get_messages(request)
            for message in system_messages:
                pass
            system_messages.used = True




class FlashcardGame(Game):
    template_name = 'flashcard.html'


    def get(self, request):

        # If session level hasn't been given a value this means the session hasn't been initialized
        # For example if user has gone straigt to flashcard url without selecting a level previously

        # initialized, created = PlayerStatus.objects.get_or_create(user=self.request.user)
        # if initialized.current_level == 0:
        #     level = [self.initializeQuiz(request),]
        #     answered_data = self.load_data(level, self.request.user)
        #     self.get_questions2(answered_data, request)
        # initialized.review_game = False
        #
        # if 'data' not in request.session:
        #     level = [self.initializeQuiz(request),]
        #     answered_data = self.load_data(level, self.request.user)
        #     self.get_questions2(answered_data, request)
        self.get_quiz_data(request, 'flashcard')

        # data = request.session['data']
        # d = json.loads(data)

        self.data = self.get_current_question(request)
        #Get current question from user status
        # status = PlayerStatus.objects.filter(user = self.request.user).first()
        # question_num = int(status.currentQuestion)
        # remainder of (question number, total number of questions)-  Serve the (remainder)th question for the level
        # This is for when there are less than 10 questions

        # try:
        #     n = int(question_num) % int(len(d))
        #     data = d[n]
        # except:
        #     level = [self.initializeQuiz(request),]
        #     answered_data = self.load_data(level, self.request.user)
        #     self.get_questions2(answered_data, request)
        #     data = request.session['data']
        #     d = json.loads(data)
        #     n = int(question_num) % int(len(d))
        #     data = d[n]

        english = Spanish.objects.filter(spanish_phrase=self.data['fields']['spanish_id']).values('english_translation').first()


        #If the question is number 1 need to clear messages


        context = {'data': self.d,
                   'number': self.data['pk'],
                   'question':english['english_translation'],
                   'question_num': self.question_num + 1,
                   'level': self.data['fields']['level'],
                   'correct': self.data['fields']['correct_answer'],
                   'options': [self.data['fields']['distractor_one'],
                               self.data['fields']['distractor_two'],
                               self.data['fields']['distractor_three'],
                               self.data['fields']['distractor_four' ],],
                   'lives':3 - (self.status.currentErrors),

                   }

        return render(request, self.template_name, context)

    def flashcard_check_answer(self,request):
        self.correct_answer = self.correct_answer.replace(u"\u00A0", " ")

        if self.answer == "timeout":
            quality = 0
            messages.error(request, "Bummer! Wrong answer, try again :(")
            self.status.currentErrors = int(self.status.currentErrors) + 1

        else:
            if self.correct_answer == self.answer:
                quality = 5

                self.status.currentScore = int(self.status.currentScore) + 1

                messages.success(request, "Yohoo! Correct answer, keep up the streak :)")
            else:
                quality = 1
                self.status.currentErrors = int(self.status.currentErrors) + 1

                # If the quality of response was lower than 3 then start repetitions from beginning
                # without changing EF
                messages.error(request, "Bummer! Wrong answer, try again :(")
        self.status.save()

        return quality


    def post(self, request):
        # question_id = int(request.POST['question-id'])
        # answer = str(request.POST['answer'])
       #answer = answer.strip()
        # answer = re.sub('&nbsp;', ' ', answer)
        # answer = answer.replace(u"\u00A0", " ")

        self.get_and_format_POST_data(request)
        # question_num = int(request.POST['question-num'])-1
        # level = int(request.POST['level'])

        #if 'data' not in request.session:       #Do I need this here??????????????
            #level = self.initializeQuiz(request)
            #answered_data = self.load_data(level, self.request.user)
            #self.get_questions2(answered_data, level, request)
        self.correct_answer = self.get_POST_correct_answer(request)
        #Get JSON data for question number
        # data = request.session['data']
        # d = json.loads(data)
        #
        # # remainder of (question number, total number of questions)-  Serve the (remainder)th question for the level
        # # This is for when there are less than 10 questions
        # n = int(question_num) % int(len(d))
        # data = d[n]

        #Get correct answer from JSON data
        #correct_answer = str(data['fields']['correct_answer'])

        self.POST_increment_current_question(request)

        # status, created = PlayerStatus.objects.get_or_create(user=self.request.user)
        # status.currentQuestion = int(self.question_num + 1)
        # status.save()

        #Update answered Model

        # spanishObj = Spanish.objects.get(spanish_phrase=self.correct_answer)
        #
        # answered, created = Answered.objects.get_or_create(user=self.request.user,
        #                                                    spanish_id =spanishObj,
        #                                                    level_int= spanishObj.level_number.level_number)



        #self.correct_answer = self.correct_answer.replace(u"\u00A0", " ")
        #status, created = PlayerStatus.objects.get_or_create(user=self.request.user)
        # If user didn't attempt then quality is 0

        self.quality = self.flashcard_check_answer(request)
        self.answered = self.POST_update_Answered_data(request)

        # if self.answer == "timeout":
        #     quality = 0
        #     messages.error(request, "Bummer! Wrong answer, try again :(")
        #     self.status.currentErrors = int(self.status.currentErrors) + 1
        #
        # else:
        #     if self.correct_answer == self.answer:
        #         quality = 5
        #
        #         self.status.currentScore = int(self.status.currentScore) + 1
        #
        #         messages.success(request, "Yohoo! Correct answer, keep up the streak :)")
        #     else:
        #         quality = 1
        #         self.status.currentErrors = int(self.status.currentErrors) + 1
        #
        #         # If the quality of response was lower than 3 then start repetitions from beginning
        #         # without changing EF
        #         messages.error(request, "Bummer! Wrong answer, try again :(")
        # self.status.save()
        #Create new sessions data of results with quality score to show in results page

        # saved_results = request.session['results']
        # if self.correct_answer not in saved_results:
        #     saved_results[self.correct_answer] = (self.quality,)
        # else:
        #     results = saved_results[self.correct_answer]
        #     results.append(self.quality)
        #     saved_results[self.correct_answer] = results
        # request.session['results'] = saved_results
        self.POST_save_to_results(request)
        self.POST_check_end_game_conditions(request)
        if self.status.currentQuestion == 10:
            system_messages = messages.get_messages(request)
            for message in system_messages:
                pass
            system_messages.used = True
            request.session['initialized'] = False
            return redirect('result')

        else:
            return redirect('flashcard')


        # result = self.updateInterval(self.answered.ef, self.answered.repetition , self.quality)
        # self.answered.ef = result[0]
        # self.answered.repetition = result[1]



        # ##If repetition is less than or more than 2 call setReview function also needs to be called
        # setreview = self.setReview (answered.repetition)
        # answered.quality_value = quality
        # answered.review_time = setreview
        # answered.last_review_day = timezone.now().date()
        #
        # answered.save()
        # if self.status.currentErrors >= 3:
        #     system_messages = messages.get_messages(request)
        #     for message in system_messages:
        #         pass
        #     system_messages.used = True
        #
        # if self.status.currentQuestion == 10:
        #     system_messages = messages.get_messages(request)
        #     for message in system_messages:
        #         pass
        #     system_messages.used = True
        #     request.session['initialized'] = False
        #     return redirect('/flashcard_result/')





class Result(LoginRequiredMixin, View):
    template_name = 'result.html'

    def update_database(self, request):
        self.status, created = PlayerStatus.objects.get_or_create(user=self.request.user)
        self.game_score = int(self.status.currentScore)

        # Add final score to playerscore
        self.user = PlayerScore.objects.get(user=self.request.user)
        self.user.score = int(self.user.score) + int(self.game_score)

        # Add game points to current level points only if the game was played in the user's top level
        if int(self.status.current_level) == int(self.user.level.level_number):
            self.user.current_level_score = self.user.current_level_score + self.game_score

        # Add session to user session
        session, created = UserSessions.objects.get_or_create(user=self.request.user,
                                                              session=datetime.datetime.now().date())
    def check_level_up(self, request):
        # If points threshold is met for level user can level up
        level_detail = Levels.objects.filter(level_number=str(self.user.level)).first()
        try:
            if self.user.current_level_score >= level_detail.points_threshold:
                # level up
                # Get next level model
                levelUp = str(self.user.level.level_number + 1)
                levelUp_detail = Levels.objects.get(level_number=levelUp)
                self.user.level = levelUp_detail
                # If level up reset current level points to zero
                self.user.current_level_score = 0
                request.session['level_up'] = True

        except:
            return redirect('home')

    def reset_status_data(self, request):
        # Reset current user details to 0
        self.status.currentQuestion = 0
        self.status.currentScore = 0
        self.status.current_level = 0
        self.status.currentErrors = 0
        self.status.save()
        self.user.save()
        request.session['data'] = ""

    def get(self,request):

        # status, created = PlayerStatus.objects.get_or_create(user=self.request.user)
        # game_score = int(status.currentScore)

        self.update_database(request)

        # #Add session to user session
        # session, created = UserSessions.objects.get_or_create(user=self.request.user,
        #                                                       session = datetime.datetime.now().date())


        # #Add final score to playerscore
        # user = PlayerScore.objects.get(user = self.request.user)
        # user.score = int(user.score) + int(game_score)
        #
        # #Add game points to current level points only if the game was played in the user's top level
        # if int(status.current_level) == int(user.level.level_number):
        #     user.current_level_score = user.current_level_score + game_score


        self.check_level_up(request)
        # #If points threshold is met for level user can level up
        # level_detail = Levels.objects.filter(level_number=str(user.level)).first()
        # try:
        #     if user.current_level_score >= level_detail.points_threshold:
        #         #level up
        #         #Get next level model
        #         levelUp = str(user.level.level_number + 1)
        #         levelUp_detail = Levels.objects.get(level_number = levelUp)
        #         user.level = levelUp_detail
        #         #If level up reset current level points to zero
        #         user.current_level_score = 0
        #         request.session['level_up'] = True
        #
        # except:
        #     return redirect('home')
        #get data results


        saved_results = request.session['results']
        self.reset_status_data(request)

        # #Reset current user details to 0
        # status.currentQuestion = 0
        # status.currentScore = 0
        # status.current_level = 0
        # status.currentErrors = 0
        # status.save()
        # user.save()
        # request.session['data'] = ""

        context = {
            'score': self.game_score,
            'data': saved_results,
            'level_up': request.session['level_up'],
            'review': self.status.review_game,
            'game': self.status.game,



        }

        return render(request, self.template_name, context)







