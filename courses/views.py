from django.shortcuts import render, redirect, render_to_response
from django.template.context_processors import request
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, DetailView, FormView
from django.urls import reverse_lazy
from .models import Levels, Spanish, PlayerStatus, PlayerScore, UserSessions
from django_filters.views import FilterView
from django.contrib.auth.decorators import login_required
import random
from flashcard.models import Answered, Questions
from django.views import View
from django.http import HttpResponse
from random import shuffle
from django.core import serializers
from django.utils import timezone
from datetime import datetime, date
from django.db.models import Q
import json
from calendar import HTMLCalendar, monthrange
from datetime import date, timedelta
from itertools import groupby
from django.utils.safestring import mark_safe
from construct.models import Verbs, Pronouns, Article
import calendar


# Create your views here.

class LoadQuestionsMixin(object):

    def load_distractors(self, spanish_phrase):
        self.user = self.request.user
        distractors = []
        i = 0
        while i < 3:
            random_object = Spanish.objects.order_by('?').values('spanish_phrase')[0]
            # check random object isn't equal to spanish
            random_object = random_object['spanish_phrase']
            if random_object not in distractors and str(random_object) != spanish_phrase:
                distractors.append(str(random_object))
                i = i + 1
        return distractors

    def load_distractors2(self,spanish_phrase):

        type = spanish_phrase.type
        level = str(spanish_phrase.level_number)
        phrase = str(spanish_phrase.spanish_phrase)
        distractors = Spanish.objects.filter(Q(type=type, level_number= level) & ~Q(spanish_phrase=phrase))[:3]
        print('first', distractors)

        #There might not always be all the same types in level
        need = 3 - (len(distractors))
        print('need', need)
        if need != 0:
            distractors2 = Spanish.objects.filter(Q(type=type) & ~Q(level_number =level))[:need]
            print('got', distractors2)
            distractors = distractors | distractors2
            print('got', distractors2)

        distractors_list = []
        for item in distractors:
            distractors_list.append(str(item.spanish_phrase))

        return distractors_list

    def load_construct_distractors(self,spanish_phrase):
        #break up the phrase
        words = spanish_phrase.spanish_phrase.split()
        if len(words) == 1:
            return

        distractors = []
        for word in words:
            word = word.strip('?¿!¡')
            word = word.lower()
            #search verbs
            verb_distractor = Verbs.objects.filter(Q(infinitive=word) | Q(yo=word) | Q(tú=word)
                                                   | Q(usted_él_ella=word) | Q(nosotros_nosotras=word)
                                                   | Q(vosotros_vosotras = word) | Q(ustedes_ellos_ellas = word)).first()
            if verb_distractor:
                random_verb_conjugations = [verb_distractor.infinitive, verb_distractor.yo, verb_distractor.tú,
                                            verb_distractor.usted_él_ella, verb_distractor.nosotros_nosotras]
                if word in random_verb_conjugations:
                    random_verb_conjugations.remove(word)
                distractors.append(random.choice(random_verb_conjugations))

            #Want to take random infinitive or conjugation

            #search pronouns
            pronoun = Pronouns.objects.filter(spanish= word).first()
            if pronoun:
                pronoun_distractor = Pronouns.objects.filter(Q(person = pronoun.person,
                                                            pronoun_type = pronoun.pronoun_type) &
                                                             ~Q(spanish = pronoun.spanish)).first()
                if pronoun_distractor:
                    distractors.append(pronoun_distractor.spanish)
                else:
                    pronoun_distractor = Pronouns.objects.filter(Q(pronoun_type=pronoun.pronoun_type) &
                                                                 ~Q(spanish=pronoun.spanish)).first()
                    if pronoun_distractor:
                        distractors.append(pronoun_distractor.spanish)
            article = Article.objects.filter(Q(spanish= word)).first()
            if article:
                article = Article.objects.filter(~Q(spanish=word)).order_by('?').first()
                distractors.append(article.spanish)

        return distractors


    def get_questions2(self, answered_data, level, request):
        # need to turn list into a list of spanish objects
        spanish = Spanish.objects.filter(spanish_phrase__in=answered_data).all()

        for item in spanish:
            question, created = Questions.objects.get_or_create(spanish_id=item)

            distract = self.load_distractors2(item)
            construct_distractors = self.load_construct_distractors(item)



            distract.append(item.spanish_phrase)
            random.shuffle(distract)

            question.level = level
            question.correct_answer = item.spanish_phrase
            question.distractor_one = distract[0]
            question.distractor_two = distract[1]
            question.distractor_three = distract[-2]
            question.distractor_four = distract[-1]
            if construct_distractors:
                question.construct_one = construct_distractors[0]
                if len(construct_distractors) > 1:
                    question.construct_two = construct_distractors[1]
                    if len(construct_distractors) > 2:
                        question.correct_three = construct_distractors[2]

            question.save()



        data = list(Questions.objects.filter(spanish_id__in=spanish).all())
        shuffle(data)

        data = serializers.serialize("json", data)
        request.session['data'] = data

        # session data for results
        results = dict()
        request.session['results'] = results

    def load_data(self, level, user):
        data = Answered.objects.filter(user=user,
                                       level_int=level,
                                       repetition=0).values('spanish_id').all()

        # Need to turn this into a list of only spanish_id
        datals = list()
        for item in data:
            datals.append(item['spanish_id'])
        # If there are atleast 10 on repetition 0
        print('0 rep', datals)
        if len(datals) >= 10:
            datals = datals[:10]
        else:
            get = 10 - (len(data))
            due = self.due_load(get, level, datals, user)
            print('due', due)
            datals = datals + due
            if len(datals) < 10:
                lessthan4 = self.quality_load(get, level, datals, user)
                print('less than 4', lessthan4)
                datals = datals + lessthan4
                if len(datals) < 10:
                    get = 10 - (len(datals))
                    remainingData = self.ranked_load(get, level, datals, user)
                    print('ranked', remainingData)
                    datals = datals + remainingData

        return datals

    def ranked_load(self, num, level, data_ls, user):
        now = timezone.now()
        check = Answered.objects.filter(user=user,
                                        level_int=level, ).values('spanish_id', 'review_time')
        # calculate differnece between now and review time and store in list
        rankings = dict()
        for item in check:
            time = item['review_time']
            spanish = item['spanish_id']
            # Check that phrase has not already been added based on repetition
            if spanish not in data_ls:
                try:
                    reviewCal = time - now
                except:
                    time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')
                    reviewCal = time - now
                rankings[spanish] = reviewCal

        # Sort list by order of review time
        # phrases are ordered smallest to largest
        rank = sorted(rankings.items(), key=lambda x: x[1])

        # slice lowest rankings in the list to add to round phrases
        data = rank[:num]
        # return only phrase IDs as a list
        phrases = [x[0] for x in data]
        return phrases

    def quality_load(self, num, level, data_ls, user):
        # Checks for items that have been reviewed today with a quality result of less than 4
        returned = list()
        today = timezone.now().date()
        check = Answered.objects.filter(user=user,
                                        level_int=level,
                                        last_review_day=today).values('spanish_id', 'quality_value')
        for item in check:
            if item['spanish_id'] not in data_ls:
                if int(item['quality_value']) < 4:
                    returned.append(item['spanish_id'])

        return returned[:num]

    def due_load(self, num, level, data_ls, user):
        # checks for items that are due today or overdue
        rankings = dict()
        returned = list()
        today = timezone.now()
        check = Answered.objects.filter(user=user,
                                        level_int=level, ).values('spanish_id', 'review_time')

        for item in check:
            if item['spanish_id'] not in data_ls:   #‘data_ls’ is items already added because they are 0 repetition.
                if item['review_time'] <= today:
                    returned.append(item['spanish_id'])
                    rankings[item['spanish_id']] = item['review_time']

        rank = sorted(rankings.items(), key=lambda x: x[1])
        rank[:num]
        phrases = [x[0] for x in rank]
        print('THIS IS RANKED DUE', phrases)

        return phrases


class InitializeMixin(object):

    def initializeQuiz(self, request):
        playerScore = PlayerScore.objects.filter(user=self.request.user).first()
        maxLevel = 1
        if int(playerScore.level.level_number) > maxLevel:
            maxLevel = int(playerScore.level.level_number)
        # Check if user has surpasses threshold points
        level_detail = Levels.objects.filter(level_number=str(maxLevel)).first()
        if int(playerScore.current_level_score) >= int(level_detail.points_threshold):
            # set the session data as levelled up so can display bootstrap level up
            request.session['level_up'] = True
            maxLevel = maxLevel + 1
            playerScore.level = maxLevel
            playerScore.save()

        # add highest level to current level
        current, created = PlayerStatus.objects.get_or_create(user=self.request.user)
        current.current_level = maxLevel
        current.save()
        return maxLevel



def streak(session_object, user, streak_length):
    date = session_object.session
    yesterday = date - timedelta(days=1)
    result = UserSessions.objects.filter(user=user,
                                             session=str(yesterday)).all()
    if len(result) == 0:
            return streak_length
    else:
        streak_length += 1
        return streak(result[0], user, streak_length)

class CourseListView(LoginRequiredMixin, LoadQuestionsMixin, View):
    template_name = 'home.html'
    login_url = 'login'


    def get(self, request):
        user = self.request.user

        # Reset current data - in case have gone straight from game
        initialized, created = PlayerStatus.objects.get_or_create(user=self.request.user)
        initialized.currentQuestion = 0
        initialized.currentScore = 0
        initialized.currentErrors = 0
        initialized.save()

        request.session['level_up'] = False



        level_and_score = PlayerScore.objects.filter(user=user).first()
        if level_and_score is None:
            levelOne = Levels.objects.get(level_number=1)
            level_and_score, created = PlayerScore.objects.get_or_create(user=user, level=levelOne)
            level_and_score.save()
        level = str(level_and_score.level)
        score = level_and_score.current_level_score
        total_score = level_and_score.score


        level_threshold = Levels.objects.filter(level_number=str(level)).first()
        level_points_threshold = level_threshold.points_threshold
        points_needed = int(level_points_threshold) - int(score)

        # Update user level if score is more than current level threshold
        if score >= level_points_threshold:
            level = str(int(level) + 1)
            level_up = Levels.objects.filter(level_number=level).first()
            level_and_score.level = level_up
            level_and_score.save()
            level_points_threshold = level_up.points_threshold

        # Find streak length
        streak_length = 1
        latest_session = UserSessions.objects.latest('session')
        current_streak = streak(latest_session, self.request.user, streak_length)
        # Update user score for longest session

        #status, created = PlayerScore.objects.get_or_create(user=self.request.user)
        if level_and_score.day_streak < current_streak:
            level_and_score.day_streak = current_streak
            level_and_score.save()

        # Find strength for each level/topic
        now = timezone.now()
        strength = dict()
        for num in range(1, int(level) + 1):
            answered = Answered.objects.filter(user=self.request.user,
                                               level_int=num, ).values('spanish_id','review_time')

            today = 0
            two_weeks = 0
            two_weeks_plus = 0
            for item in answered:
                # If item needs to be reviewed in the next day
                if item['review_time'] < (now + timedelta(days=1)):
                    today += 1
                # If item needs to be reviewed in the next week
                elif item['review_time'] < (now + timedelta(days=14)):
                    two_weeks += 1
                elif item['review_time'] < (now + timedelta(days=14)):
                    two_weeks_plus += 1
            # If more than 3 words need to be reviewed today the topic strenght is week
            if today >= 3:
                strength[num] = 'weak'
            elif today < 3 and two_weeks >= 3:
                strength[num] = 'medium'
            elif two_weeks_plus > 3:
                strength[num] = 'high'
            else:
                strength[num] = 'weak'

        context = {
            'user': user,
            'level': level,
            'total_score': total_score,
            'level_threshold': level_points_threshold,
            'points': points_needed,
            'strength': strength,
            'level_description': level_threshold.description
        }

        return render(request, self.template_name, context)

    def post(self, request):
        current, created = PlayerStatus.objects.get_or_create(user=self.request.user)
        level_and_score = PlayerScore.objects.filter(user=request.user).first()
        if 'level_1.x' in request.POST:
            current.current_level = 1
            current.save()
            answered_data = self.load_data(1, self.request.user)
            questions = self.get_questions2(answered_data, 1, request)
            return redirect('courses/level_info/')
        if 'level_2.x' in request.POST:
            if level_and_score.level.level_number < 2:
                return redirect('/')
            current.current_level = 2
            current.save()
            answered_data = self.load_data(2, self.request.user)
            self.get_questions2(answered_data, 2, request)
            return redirect('courses/level_info/')
        if 'level_3.x' in request.POST:
            if level_and_score.level.level_number < 3:
                return redirect('/')
            current.current_level = 3
            current.save()
            answered_data = self.load_data(3, self.request.user)
            self.get_questions2(answered_data, 3, request)
            return redirect('courses/level_info/')
        if 'level_4.x' in request.POST:
            if level_and_score.level.level_number < 4:
                return redirect('/')
            current.current_level = 4
            current.save()
            answered_data = self.load_data(4, self.request.user)
            self.get_questions2(answered_data, 4, request)
            return redirect('courses/level_info/')
        if 'level_5.x' in request.POST:
            if level_and_score.level.level_number < 5:
                return redirect('/')
            current.current_level = 5
            current.save()
            answered_data = self.load_data(5, self.request.user)
            self.get_questions2(answered_data, 5, request)
            return redirect('courses/level_info/')
        else:
            return HttpResponse(request.POST)


class SessionCalendar(LoginRequiredMixin, HTMLCalendar):

    def __init__(self, sessions):
        super(SessionCalendar, self).__init__()
        self.sessions = self.group_by_day(sessions)



    def formatday(self, day, weekday):

        if day != 0:
            cssclass = self.cssclasses[weekday]
            if date.today() == date(self.year, self.month, day):
                cssclass += ' today'
            if day in self.sessions:
                cssclass += ' filled'

                return self.day_cell(cssclass, '%d' % (day))
            return self.day_cell(cssclass, day)
        return self.day_cell('noday', '')

    def formatmonth(self, year, month):
        self.year = year
        self.month = month

        return super(SessionCalendar, self).formatmonth(year, month)


    def group_by_day(self, psessions):
        field = lambda session: session.session.day


        return dict(
            [(day, list(items)) for day, items in groupby(psessions, field)]
        )

    def day_cell(self, cssclass, body):
        return '<td class="%s">%s</td>' % (cssclass, body)



class UserCourses(LoginRequiredMixin, View):
    template_name = 'profile.html'

    def get(self, request, **kwargs):
        all_sessions = UserSessions.objects.filter(user=self.request.user)
        session_arr = []


        try:
            year = self.kwargs['year']
            month = self.kwargs['month']
        except:
            today = datetime.now()
            year = int(today.year)
            month = int(today.month)

        calendarFromMonth = datetime(year, month, 1)
        calendarToMonth = datetime(year, month, monthrange(year, month)[1])
        sessionEvents = UserSessions.objects.filter(user = self.request.user,
                                                     session__gte=calendarFromMonth, session__lte=calendarToMonth)
        Calendar = SessionCalendar(sessionEvents).formatmonth(year, month)
        previousYear = year
        previousMonth = month - 1
        if previousMonth == 0:
            previousMonth = 12
            previousYear = year - 1
        nextYear = year
        nextMonth = month + 1
        if nextMonth == 13:
            nextMonth = 1
            nextYear = year + 1
        yearAfterThis = year + 1
        yearBeforeThis = year - 1

        date = str(timezone.now().date())
        latest_session = UserSessions.objects.filter(session = date).first()
        streak_length = 1
        if latest_session:
            current_streak = streak(latest_session, self.request.user, streak_length)
        else:
            current_streak = 0
        longest_streak = PlayerScore.objects.filter(user=self.request.user).values('day_streak')[0]

        context = {
            'course_list': PlayerScore.objects.filter(user=self.request.user),
            'user': self.request.user,
            #'all_sessions': all_sessions,
            #'dates': json.dumps(session_arr),
            'Calendar': mark_safe(Calendar),
            'Month': month,
            'MonthName': calendar.month_name[month],
            'Year': year,
            'PreviousMonth': previousMonth,
            'PreviousMonthName': calendar.month_name[previousMonth],
            'PreviousYear': previousYear,
            'NextMonth': nextMonth,
            'NextMonthName': calendar.month_name[nextMonth],
            'NextYear': nextYear,
            'YearBeforeThis': yearBeforeThis,
            'YearAfterThis': yearAfterThis,
            'current_streak': current_streak,
            'longest_streak': longest_streak,

        }
        return render(request, self.template_name, context)


class LevelInfo(LoginRequiredMixin, LoadQuestionsMixin, InitializeMixin, View):
    # Need to change how quiz questions are selected, this is called everytime this page is loaded based on answered
    # Need to create question table based on questions selected. Distractors need to be updated each time.

    template_name = 'level_info.html'
    login_url = 'login'

    def get(self, request):
        # If session level hasn't been given a value this means the session hasn't been initialized
        # For example if user has gone straigt to level info url without selecting a level previously
        initialized, created = PlayerStatus.objects.get_or_create(user=self.request.user)
        initialized.currentQuestion = 0
        initialized.currentScore = 0
        initialized.currentErrors = 0
        initialized.save()



        #f results is not empty it means that user has already started playing round and questions need to be reset to empty
        result = request.session['results']
        if bool(result) == True:
            #results is not empty - reset
            results = dict()
            request.session['results'] = results
            level = initialized.current_level
            answered_data = self.load_data(level, self.request.user)
            self.get_questions2(answered_data, level, request)
            print('user quit game before ending')

        if initialized.current_level == 0:
            level = self.initializeQuiz(request)
            answered_data = self.load_data(level, self.request.user)
            self.get_questions2(answered_data, level, request)
            print('had not been intialized')

        level = PlayerStatus.objects.filter(user=self.request.user).first()
        current_level = int(level.current_level)
        spanish_list = Spanish.objects.filter(level_number=current_level)
        level_desc = Levels.objects.filter(level_number=current_level).first()
        level_desc = level_desc.description

        # Need to create answered objects if not already existing for user and level
        for item in spanish_list:
            spanish = Spanish.objects.get(spanish_phrase=item)
            answered, created = Answered.objects.get_or_create(user=self.request.user,
                                                               spanish_id=spanish,
                                                               level_int=spanish.level_number.level_number)
            answered.save()

        # Get review time for each item
        # Count number of items with additional information also (i)
        i = 0
        ready_to_review = list()
        #answeredstuff = Answered.objects.filter(parent__in=spanish_list)

        #answeredstuff = Answered.objects.all().select_related("user")
        today = timezone.now()
        answeredstuff = Answered.objects.filter(spanish_id__level_number__level_number=current_level)
        answeredstuff = answeredstuff.filter(user=self.request.user)
        for item in answeredstuff:
             review = item.review_time
             due = review - today
             due = due.days
             ls = (item.spanish_id, due)
             ready_to_review.append(ls)
             if str(spanish.information) != '':
                 i =i +1


        #
        # for item in spanish_list:
        #     spanish = Spanish.objects.get(spanish_phrase=item)
        #     answer = Answered.objects.filter(user=self.request.user,
        #                                      spanish_id=spanish).first()
        #     review = answer.review_time
        #     today = timezone.now()
        #     due = review - today
        #     due = due.days
        #     ls = (spanish.spanish_phrase, due)
        #     ready_to_review.append(ls)
        #     if str(spanish.information) != '':
        #         i =i +1





        #convert queryset to dictionary

        table_words= [{'spanish_phrase': obj.spanish_phrase,
                       'english_translation': obj.english_translation,
                       'information': obj.information} for obj in spanish_list]

        for item in table_words:
            for obj in ready_to_review:
                if str(item['spanish_phrase']) == str(obj[0]):
                    item['review_in'] = obj[1]

        spanish_data = request.session['data']

        context = {
            'level': current_level,
            'level_now': level,
            'session_data': spanish_data,
            'description': level_desc,
            'NumWords': len(spanish_list),
            'level_up': request.session['level_up'],
            'ready_to_review': ready_to_review,
            'table_words': table_words,
            'NumInfo': i,
        }

        return render(request, self.template_name, context)


class ScoreBoard(View):
    template_name = 'scoreboard.html'

    def get(self, request):
        users = PlayerScore.objects.all()
        userDict = dict()
        for item in users:
            userDict[item.user] = [item.score, ]

        rankedUsers = sorted(userDict.items(), key=lambda x: x[1], reverse=True)

        for key in userDict:
            days = PlayerScore.objects.filter(user=key).first()
            day = getattr(days, 'day_streak')
            userDict[key].append(day)

        context = {
            'users': len(rankedUsers),
            'ranked': rankedUsers,

        }

        return render(request, self.template_name, context)
