from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from courses.views import LoadQuestionsMixin
from courses.models import PlayerScore, PlayerStatus, Spanish
import json
from random import sample
from django.contrib import messages
import re
from flashcard.models import Answered
from django.utils import timezone
from construct.views import CompareMixin, ConstructGame
from flashcard.views import UpdateItemsMixin, Game, FlashcardGame
# Create your views here.
class ReviewGame(ConstructGame, FlashcardGame):

    def get_quiz_data(self, request):
        self.status = PlayerStatus.objects.filter(user=self.request.user).first()
        self.status.review_game = True

        if self.status.currentQuestion == 0:
             max = PlayerScore.objects.filter(user=self.request.user).first()
             max_level = int(max.level.level_number)
             self.status.current_level = max_level

             #Make a list of levels up to a user's max level
             levels = list(range(1, max_level+1))

             #get quiz data for all levels user has access to
             answered_data = self.load_data(levels, self.request.user)
             self.get_questions2(answered_data, request)
        #
        if 'data' not in request.session:
            level = [self.initializeQuiz(request),]
            answered_data = self.load_data(level, self.request.user)
            self.get_questions2(answered_data, request)
        self.status.save()




    def get(self,request):
        #Level isn't based on current level - list of all levels up to user max level
        self.template_name = 'flashcard.html'



        self.get_quiz_data(request)



        #Homepage sets current question as zero. Therefore if user quits early and goes back to homepage,
        #then plays again, new data is created each time



        self.data = self.get_current_question(request)
        # data = request.session['data']
        # d = json.loads(data)
        #
        # # Get current question from user status
        # question_num = int(self.status.currentQuestion)
        # # remainder of (question number, total number of questions)-  Serve the (remainder)th question for the level
        # # This is for when there are less than 10 questions
        #
        # try:
        #     n = int(question_num) % int(len(d))
        #     data = d[n]
        # except:
        #     level = [self.initializeQuiz(request), ]
        #     answered_data = self.load_data(level, self.request.user)
        #     self.get_questions2(answered_data, request)
        #     data = request.session['data']
        #     d = json.loads(data)
        #     n = int(question_num) % int(len(d))
        #     data = d[n]
        #
        # english = Spanish.objects.filter(spanish_phrase=data['fields']['spanish_id']).values(
        #     'english_translation').first()
        #This view plays either flashcard or construct game
        #Modulo division by question number for even and odd question (odd is flashcard, even is construct)

        if self.question_num % 2 == 0:
            self.template_name = 'construct.html'
            self.make_option_buttons(request)
            # #This is taken from construct
            # #spanish = self.data['fields']['spanish_id']
            #
            # # This makes a list of spanish split into elements in order to decide if it should be split by character of word
            # spanishwords = self.spanish.split()
            # # if len(spanishwords) > 2 and question_num % 3 != 1:
            # if len(spanishwords) > 1:
            #     if '?' in self.spanish:
            #         spanishwords = self.spanish[1:-1].split()
            #         spanishwords = spanishwords + ['?', '¿']
            #     words = set(spanishwords)
            #     # Get phrase distractors if exist
            #     if self.data['fields']['construct_one'] != '':
            #         words.add(self.data['fields']['construct_one'])
            #         if self.data['fields']['construct_two'] != '':
            #             words.add(self.data['fields']['construct_two'])
            #             if words.add(self.data['fields']['construct_three']) != '':
            #                 words.add(self.data['fields']['construct_one'])
            #     self.p = sample(words, (len(words)))
            #     sentence = True
            #
            # # buttons for letters
            # else:
            #     characters = set(self.spanish)
            #     self.p = sample(characters, (len(characters)))
            #
            #     sentence = False

            context = {
                'question': self.english['english_translation'],
                'spanish': self.spanish,
                'spanish_words': self.p,
                'characters': self.p,
                'question_num': self.question_num + 1,
                'number': self.data['pk'],
                'word_length': len(self.p),
                'sentence': self.sentence,
                'level': self.data['fields']['level'],
                'lives': 3- (self.status.currentErrors),
                'review': True
            }

        else:

            context = {
                'data': self.d,
                'number': self.data['pk'],
                'question':self.english['english_translation'],
                'question_num': self.question_num + 1,
                'level': self.data['fields']['level'],
                'correct': self.data['fields']['correct_answer'],
                'options': [self.data['fields']['distractor_one'],
                               self.data['fields']['distractor_two'],
                               self.data['fields']['distractor_three'],
                               self.data['fields']['distractor_four' ],],
                'lives':3 - (self.status.currentErrors),
                'review': True
                }

        return render(request, self.template_name, context)

    def post(self, request):

        # answer = request.POST['answer']
        #
        # # Need to check for extra spacing between words also
        # answer = re.sub(' +', ' ', answer)
        self.get_and_format_POST_data(request)
        # Get JSON data for question number
        # data = request.session['data']
        # d = json.loads(data)

        # question_num = int(request.POST['question-num']) - 1
        # level = int(request.POST['level'])

        # remainder of (question number, total number of questions)-  Serve the (remainder)th question for the level
        # # This is for when there are less than 10 questions
        #         # n = int(self.question_num) % int(len(d))
        #         # data = d[n]
        #         #
        #         # # Get correct answer from JSON data
        #         # correct_answer = data['fields']['correct_answer']
        self.correct_answer = self.get_POST_correct_answer(request)

        # status, created = PlayerStatus.objects.get_or_create(user=self.request.user)
        # status.currentQuestion = int(self.question_num + 1)
        # status.save()
        self.POST_increment_current_question(request)


        # # Update answered Model
        #
        # spanishObj = Spanish.objects.get(spanish_phrase=correct_answer)
        #
        # answered, created = Answered.objects.get_or_create(user=self.request.user,
        #                                                    spanish_id=spanishObj,
        #                                                    level_int=spanishObj.level_number.level_number)

        #This is where check if construct or flashcard
        if self.question_num % 2 == 0:
            self.format_answer_and_target_before_comparing(request)

            self.quality = self.findQuality(self.answer, self.correct_answer2, self.sentence)
            self.check_answer(request, self.quality)
            # #CONSTRUCT
            # sentence = request.POST.get('sentence', False)
            #
            # correct_answer2 = correct_answer
            # # Remove punctuation from correct answer if missing from answer
            # if correct_answer.startswith('¿' or '¡'):
            #     if not answer.startswith('¿' or '¡'):
            #         correct_answer2 = correct_answer[1:-1]
            #
            # answer = answer.lower()
            # correct_answer2 = correct_answer2.lower()
            # quality = self.findQuality(answer, correct_answer, sentence)
            #
            # if correct_answer2 == answer:
            #     status, created = PlayerStatus.objects.get_or_create(user=self.request.user)
            #     status.currentScore = int(status.currentScore) + 2
            #     status.save()
            #     messages.success(request, "Yohoo! Correct answer, keep up the streak :)")
            # elif quality == 4:
            #     status.currentScore = int(status.currentScore) + 1
            #     status.save()
            #     messages.error(request, "Almost there! Try again :(")
            # else:
            #     status.currentErrors += 1
            #     status.save()
            #     messages.error(request, "Bummer! Wrong answer, try again :(")
            #

        else:
            self.quality = self.flashcard_check_answer(request)
            # if answer == "timeout":
            #     quality = 0
            #     messages.error(request, "Bummer! Wrong answer, try again :(")
            #     status.currentErrors = int(status.currentErrors) + 1
            #
            # else:
            #     if correct_answer == answer:
            #         quality = 5
            #
            #         status.currentScore = int(status.currentScore) + 1
            #
            #         messages.success(request, "Yohoo! Correct answer, keep up the streak :)")
            #     else:
            #         quality = 1
            #         status.currentErrors = int(status.currentErrors) + 1
            #
            #         # If the quality of response was lower than 3 then start repetitions from beginning
            #         # without changing EF
            #         messages.error(request, "Bummer! Wrong answer, try again :(")
            # status.save()
        # Create new sessions data of results with quality score to show in results page
        print(self.correct_answer)
        self.answered = self.POST_update_Answered_data(request)
        self.POST_save_to_results(request)
        # saved_results = request.session['results']
        # if self.correct_answer not in saved_results:
        #     saved_results[self.correct_answer] = (self.quality,)
        # else:
        #     results = saved_results[self.correct_answer]
        #     results.append(self.quality)
        #     saved_results[self.correct_answer] = results
        # request.session['results'] = saved_results
        # print(request.session['results'])

        # result = self.updateInterval(answered.ef, answered.repetition, quality)
        # answered.ef = result[0]
        # answered.repetition = result[1]
        #
        # review = self.setReview(answered.repetition)
        # answered.review_time = review
        # answered.quality_value = quality
        # answered.last_review_day = timezone.now().date()
        # answered.save()
        self.POST_check_end_game_conditions(request)
        # if status.currentErrors >= 3:
        #     system_messages = messages.get_messages(request)
        #     for message in system_messages:
        #         pass
        #     system_messages.used = True

        if self.status.currentQuestion == 10:
            system_messages = messages.get_messages(request)
            for message in system_messages:
                pass
            system_messages.used = True
            request.session['initialized'] = False
            return redirect('result')


        return redirect('review')

