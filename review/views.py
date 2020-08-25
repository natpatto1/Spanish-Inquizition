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
from construct.views import CompareMixin
from flashcard.views import UpdateItemsMixin
# Create your views here.
class ReviewGame(LoginRequiredMixin, View, LoadQuestionsMixin, CompareMixin, UpdateItemsMixin):

    def get(self,request):
        #Level isn't based on current level - list of all levels up to user max level
        self.template_name = 'flashcard.html'
        status = PlayerStatus.objects.filter(user=self.request.user).first()
        status.review_game = True


        #Homepage sets current question as zero. Therefore if user quits early and goes back to homepage,
        #then plays again, new data is created each time

        if status.currentQuestion == 0:
            max = PlayerScore.objects.filter(user=self.request.user).first()
            max_level = int(max.level.level_number)
            status.current_level = max_level

            #Make a list of levels up to a user's max level
            levels = list(range(1, max_level+1))

            #get quiz data for all levels user has access to
            answered_data = self.load_data(levels, self.request.user)
            self.get_questions2(answered_data, request)

        if 'data' not in request.session:
            level = [self.initializeQuiz(request),]
            answered_data = self.load_data(level, self.request.user)
            self.get_questions2(answered_data, request)

        status.save()
        data = request.session['data']
        d = json.loads(data)

        # Get current question from user status
        question_num = int(status.currentQuestion)
        # remainder of (question number, total number of questions)-  Serve the (remainder)th question for the level
        # This is for when there are less than 10 questions

        try:
            n = int(question_num) % int(len(d))
            data = d[n]
        except:
            level = [self.initializeQuiz(request), ]
            answered_data = self.load_data(level, self.request.user)
            self.get_questions2(answered_data, request)
            data = request.session['data']
            d = json.loads(data)
            n = int(question_num) % int(len(d))
            data = d[n]

        english = Spanish.objects.filter(spanish_phrase=data['fields']['spanish_id']).values(
            'english_translation').first()
        #This view plays either flashcard or construct game
        #Modulo division by question number for even and odd question (odd is flashcard, even is construct)

        if question_num % 2 == 0:
            self.template_name = 'construct.html'
            #This is taken from construct
            spanish = data['fields']['spanish_id']

            # This makes a list of spanish split into elements in order to decide if it should be split by character of word
            spanishwords = spanish.split()
            # if len(spanishwords) > 2 and question_num % 3 != 1:
            if len(spanishwords) > 1:
                if '?' in spanish:
                    spanishwords = spanish[1:-1].split()
                    spanishwords = spanishwords + ['?', '¿']
                words = set(spanishwords)
                # Get phrase distractors if exist
                if data['fields']['construct_one'] != '':
                    words.add(data['fields']['construct_one'])
                    if data['fields']['construct_two'] != '':
                        words.add(data['fields']['construct_two'])
                        if words.add(data['fields']['construct_three']) != '':
                            words.add(data['fields']['construct_one'])
                p = sample(words, (len(words)))
                sentence = True

            # buttons for letters
            else:
                characters = set(spanish)
                p = sample(characters, (len(characters)))

                sentence = False

            context = {
                'question': english['english_translation'],
                'spanish': spanish,
                'spanish_words': spanishwords,
                'characters': p,
                'question_num': question_num + 1,
                'number': data['pk'],
                'word_length': len(p),
                'sentence': sentence,
                'level': data['fields']['level'],
                'lives': 3- (status.currentErrors),
                'review': True
            }

        else:

            context = {
                'data': d,
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
                'review': True
                }

        return render(request, self.template_name, context)

    def post(self, request):

        answer = request.POST['answer']

        # Need to check for extra spacing between words also
        answer = re.sub(' +', ' ', answer)

        # Get JSON data for question number
        data = request.session['data']
        d = json.loads(data)

        question_num = int(request.POST['question-num']) - 1
        level = int(request.POST['level'])

        # remainder of (question number, total number of questions)-  Serve the (remainder)th question for the level
        # This is for when there are less than 10 questions
        n = int(question_num) % int(len(d))
        data = d[n]

        # Get correct answer from JSON data
        correct_answer = data['fields']['correct_answer']

        status, created = PlayerStatus.objects.get_or_create(user=self.request.user)
        status.currentQuestion = int(question_num + 1)
        status.save()

        # Update answered Model

        spanishObj = Spanish.objects.get(spanish_phrase=correct_answer)

        answered, created = Answered.objects.get_or_create(user=self.request.user,
                                                           spanish_id=spanishObj,
                                                           level_int=spanishObj.level_number.level_number)

        #This is where check if construct or flashcard
        if question_num % 2 == 0:
            #CONSTRUCT
            sentence = request.POST.get('sentence', False)

            correct_answer2 = correct_answer
            # Remove punctuation from correct answer if missing from answer
            if correct_answer.startswith('¿' or '¡'):
                if not answer.startswith('¿' or '¡'):
                    correct_answer2 = correct_answer[1:-1]

            answer = answer.lower()
            correct_answer2 = correct_answer2.lower()
            quality = self.findQuality(answer, correct_answer, sentence)

            if correct_answer2 == answer:
                status, created = PlayerStatus.objects.get_or_create(user=self.request.user)
                status.currentScore = int(status.currentScore) + 2
                status.save()
                messages.success(request, "Yohoo! Correct answer, keep up the streak :)")
            elif quality == 4:
                status.currentScore = int(status.currentScore) + 1
                status.save()
                messages.error(request, "Almost there! Try again :(")
            else:
                status.currentErrors += 1
                status.save()
                messages.error(request, "Bummer! Wrong answer, try again :(")


        else:
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
        # Create new sessions data of results with quality score to show in results page

        saved_results = request.session['results']
        if correct_answer not in saved_results:
            saved_results[correct_answer] = (quality,)
        else:
            results = saved_results[correct_answer]
            results.append(quality)
            saved_results[correct_answer] = results
        request.session['results'] = saved_results

        result = self.updateInterval(answered.ef, answered.repetition, quality)
        answered.ef = result[0]
        answered.repetition = result[1]

        review = self.setReview(answered.repetition)
        answered.review_time = review
        answered.quality_value = quality
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


        return redirect('review')

