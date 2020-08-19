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


class FlashcardGame(LoginRequiredMixin, LoadQuestionsMixin, InitializeMixin,UpdateItemsMixin, View):
    template_name = 'flashcard.html'


    def get(self, request):

        # If session level hasn't been given a value this means the session hasn't been initialized
        # For example if user has gone straigt to flashcard url without selecting a level previously

        initialized, created = PlayerStatus.objects.get_or_create(user=self.request.user)
        if initialized.current_level == 0:
            level = self.initializeQuiz(request)
            answered_data = self.load_data(level, self.request.user)
            self.get_questions2(answered_data, level, request)
            print('had not been intialized')

        if 'data' not in request.session:
            level = self.initializeQuiz(request)
            answered_data = self.load_data(level, self.request.user)
            self.get_questions2(answered_data, level, request)


        data = request.session['data']
        d = json.loads(data)


        #Get current question from user status
        status = PlayerStatus.objects.filter(user = self.request.user).first()
        question_num = int(status.currentQuestion)
        # remainder of (question number, total number of questions)-  Serve the (remainder)th question for the level
        # This is for when there are less than 10 questions

        try:
            n = int(question_num) % int(len(d))
            data = d[n]
        except:
            level = self.initializeQuiz(request)
            answered_data = self.load_data(level, self.request.user)
            self.get_questions2(answered_data, level, request)
            data = request.session['data']
            d = json.loads(data)
            n = int(question_num) % int(len(d))
            data = d[n]

        english = Spanish.objects.filter(spanish_phrase=data['fields']['spanish_id']).values('english_translation').first()


        #If the question is number 1 need to clear messages


        context = {'data': d,
                   'number': data['pk'],
                   'question':english['english_translation'],
                   'question_num': question_num + 1,
                   'level': data['fields']['level'],
                   'correct': data['fields']['correct_answer'],
                   'options': [data['fields']['distractor_one'],
                               data['fields']['distractor_two'],
                               data['fields']['distractor_three'],
                               data['fields']['distractor_four' ],],
                   'lives':3 - (status.currentErrors),
                   }

        return render(request, self.template_name, context)




    def post(self, request):
        question_id = int(request.POST['question-id'])
        answer = request.POST['answer']
        print('answer',answer)
        answer = answer.strip()

        question_num = int(request.POST['question-num'])-1
        level = int(request.POST['level'])

        if 'data' not in request.session:
            level = self.initializeQuiz(request)
            answered_data = self.load_data(level, self.request.user)
            self.get_questions2(answered_data, level, request)
        #Get JSON data for question number
        data = request.session['data']
        d = json.loads(data)

        # remainder of (question number, total number of questions)-  Serve the (remainder)th question for the level
        # This is for when there are less than 10 questions
        n = int(question_num) % int(len(d))
        data = d[n]

        #Get correct answer from JSON data
        correct_answer = data['fields']['correct_answer']

        status, created = PlayerStatus.objects.get_or_create(user=self.request.user)
        status.currentQuestion = int(question_num + 1)
        status.save()

        #Update answered Model

        spanishObj = Spanish.objects.get(spanish_phrase=correct_answer)

        answered, created = Answered.objects.get_or_create(user=self.request.user,
                                                           spanish_id =spanishObj,
                                                           level_int= spanishObj.level_number.level_number)

        status, created = PlayerStatus.objects.get_or_create(user=self.request.user)
        # If user didn't attempt then quality is 0
        if answer == "timeout":
            quality = 0
            messages.error(request, "Bummer! Wrong answer, try again :(")
            status.currentErrors = int(status.currentErrors) + 1

        else:
            if correct_answer == answer:
                quality = 5

                status.currentScore = int(status.currentScore) + 1

                messages.success(request, "Yohoo! Correct answer, keep up the streak :)")
            else:
                quality = 1
                status.currentErrors = int(status.currentErrors) + 1

                # If the quality of response was lower than 3 then start repetitions from beginning
                # without changing EF
                messages.error(request, "Bummer! Wrong answer, try again :(")
        status.save()
        #Create new sessions data of results with quality score to show in results page

        saved_results = request.session['results']
        if correct_answer not in saved_results:
            saved_results[correct_answer] = (quality,)
        else:
            results = saved_results[correct_answer]
            results.append(quality)
            saved_results[correct_answer] = results
        request.session['results'] = saved_results



        result = self.updateInterval(answered.ef, answered.repetition , quality)
        answered.ef = result[0]
        answered.repetition = result[1]



        ##If repetition is less than or more than 2 call setReview function also needs to be called
        setreview = self.setReview (answered.repetition)
        answered.quality_value = quality
        answered.review_time = setreview
        answered.last_review_day = timezone.now().date()

        answered.save()
        if status.currentErrors >= 3:
            system_messages = messages.get_messages(request)
            for message in system_messages:
                pass
            system_messages.used = True

        if status.currentQuestion == 10:
            system_messages = messages.get_messages(request)
            for message in system_messages:
                pass
            system_messages.used = True
            request.session['initialized'] = False
            return redirect('/flashcard_result/')


        return redirect('flashcard')


class FlashcardResult(LoginRequiredMixin, View):
    template_name = 'flashcard_result.html'

    def get(self,request):
        status, created = PlayerStatus.objects.get_or_create(user=self.request.user)
        game_score = int(status.currentScore)
        print('game_score', game_score)

        #Add session to user session
        session, created = UserSessions.objects.get_or_create(user=self.request.user,
                                                              session = datetime.datetime.now().date())


        #Add final score to playerscore
        user = PlayerScore.objects.get(user = self.request.user)
        user.score = int(user.score) + int(game_score)

        #Add game points to current level points only if the game was played in the user's top level
        if int(status.current_level) == int(user.level.level_number):
            user.current_level_score = user.current_level_score + game_score



        #If points threshold is met for level user can level up
        level_detail = Levels.objects.filter(level_number=str(user.level)).first()
        try:
            if user.current_level_score >= level_detail.points_threshold:
                #level up
                #Get next level model
                levelUp = str(user.level.level_number + 1)
                levelUp_detail = Levels.objects.get(level_number = levelUp)
                user.level = levelUp_detail
                #If level up reset current level points to zero
                user.current_level_score = 0
                request.session['level_up'] = True

        except:
            return redirect('home')
        #get data results


        saved_results = request.session['results']


        #Reset current user details to 0
        status.currentQuestion = 0
        status.currentScore = 0
        status.current_level = 0
        status.currentErrors = 0
        status.save()
        user.save()
        request.session['data'] = ""

        context = {
            'score': game_score,
            'data': saved_results,
            'level_up': request.session['level_up'],



        }

        return render(request, self.template_name, context)





class GameOver(LoginRequiredMixin,View):
    template_name = 'gameover.html'





    def get(self, request):

        if 'results' not in request.session:
            request.session['resuls'] = dict()


        initialized, created = PlayerStatus.objects.get_or_create(user=self.request.user)
        initialized.currentQuestion = 0
        initialized.currentScore = 0
        initialized.currentErrors = 0
        initialized.current_level = 0
        initialized.save()
        results = dict()
        request.session['results'] = results
        context = {


        }
        return render(request, self.template_name, context)







