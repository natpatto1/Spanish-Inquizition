from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Levels, Spanish, PlayerStatus, PlayerScore, UserSessions
import random
from flashcard.models import Answered, Questions
from django.views import View
from django.http import HttpResponse
from random import shuffle
from django.core import serializers
from django.utils import timezone
from datetime import datetime, date
from django.db.models import Q
from calendar import HTMLCalendar, monthrange
from datetime import date, timedelta
from itertools import groupby
from django.utils.safestring import mark_safe
from construct.models import Verbs, Pronouns, Article
import calendar


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


        #There might not always be all the same types in level
        need = 3 - (len(distractors))

        if need != 0:
            distractors2 = Spanish.objects.filter(Q(type=type) & ~Q(level_number =level))[:need]

            distractors = distractors | distractors2


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


    def get_questions2(self, answered_data, request):
        # need to turn list into a list of spanish objects
        spanish = Spanish.objects.filter(spanish_phrase__in=answered_data).all()

        for item in spanish:
            question, created = Questions.objects.get_or_create(spanish_id=item,
                                                                level = item.level_number.level_number)

            distract = self.load_distractors2(item)
            construct_distractors = self.load_construct_distractors(item)

            distract.append(item.spanish_phrase)
            random.shuffle(distract)


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
        self.data = Answered.objects.filter(user=user,
                                       level_int__in =level).all()
        #zero_rep = self.data.filter(repetition=0).values('spanish_id').all()
        # Need to turn this into a list of only spanish_id
        datals = list()
        for item in self.data:
            if item.repetition == 0:
                datals.append(item.spanish_id)
        # If there are atleast 10 on repetition 0

        if len(datals) >= 10:
            datals = datals[:10]
        else:
            get = 10 - (len(datals))
            due = self.due_load(get, level, datals, user)

            datals = datals + due
            if len(datals) < 10:
                lessthan4 = self.quality_load(get, level, datals, user)

                datals = datals + lessthan4
                if len(datals) < 10:
                    get = 10 - (len(datals))
                    remainingData = self.ranked_load(get, level, datals, user)

                    datals = datals + remainingData

        return datals

    def ranked_load(self, num, level, data_ls, user):
        now = timezone.now()
        # check = Answered.objects.filter(user=user,
        #                                 level_int__in=level, ).values('spanish_id', 'review_time')
        # calculate differnece between now and review time and store in list
        rankings = dict()
        for item in self.data:
            time = item.review_time
            spanish = item.spanish_id
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
        # check = Answered.objects.filter(user=user,
        #                                 level_int__in=level,
        #                                 last_review_day=today).values('spanish_id', 'quality_value')
        for item in self.data:
            if item.last_review_day == today:
                if item.spanish_id not in data_ls:
                    if int(item.quality_value) < 4:
                        returned.append(item.spanish_id)

        return returned[:num]

    def due_load(self, num, level, data_ls, user):
        # checks for items that are due today or overdue
        rankings = dict()
        returned = list()
        today = timezone.now()
        # check = Answered.objects.filter(user=user,
        #                                 level_int__in=level, ).values('spanish_id', 'review_time')

        for item in self.data:
            if item.spanish_id not in data_ls:   #‘data_ls’ is items already added because they are 0 repetition.
                if item.review_time <= today:
                    returned.append(item.spanish_id)
                    rankings[item.spanish_id] = item.review_time

        rank = sorted(rankings.items(), key=lambda x: x[1])
        rank[:num]
        phrases = [x[0] for x in rank]


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

class CourseListView(LoginRequiredMixin, LoadQuestionsMixin, View):
    template_name = 'home.html'
    login_url = 'login'

    def create_answered_data(self, spanish_list):
        # Need to create answered objects if not already existing for user and level
        for item in spanish_list:

            answered, created = Answered.objects.get_or_create(user=self.user,
                                                               spanish_id=item,
                                                               level_int=item.level_number.level_number)
            answered.save()


    def streak(self, session_object, streak_length):
        date = session_object.session
        yesterday = date - timedelta(days=1)
        result = UserSessions.objects.filter(user=self.user,
                                             session=str(yesterday)).all()

        if len(result) == 0:
            return streak_length
        else:
            streak_length += 1
            return self.streak(result[0], streak_length)

    def find_streak_length(self):
        streak_length = 0
        try:
            latest_session = UserSessions.objects.filter(user=self.user).latest('session')
            self.first_time = False
            streak_length = 1
            self.current_streak = self.streak(latest_session, streak_length)
        except:
            self.first_time = True
            self.current_streak = streak_length

        # Update user score for longest session

        # status, created = PlayerScore.objects.get_or_create(user=self.request.user)
        if self.level_and_score.day_streak < self.current_streak:
            self.level_and_score.day_streak = self.current_streak
            self.level_and_score.save()

    def strength(self, level):
        now = timezone.now()
        strength = dict()

        for num in range(1, int(level) + 1):
            answered = Answered.objects.filter(user=self.user,
                                               level_int=num, ).values('spanish_id', 'review_time')

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
                elif item['review_time'] > (now + timedelta(days=14)):
                    two_weeks_plus += 1
            # If more than 3 words need to be reviewed today the topic strenght is week
            if today >= 3:
                strength[num] = 'weak'
            elif today < 3 and two_weeks >= 3:
                strength[num] = 'medium'
            elif two_weeks_plus > 3:
                strength[num] = 'strong'
            else:
                strength[num] = 'weak'

        return strength

    def create_player_score_data(self):
        self.level_and_score = PlayerScore.objects.filter(user=self.user).first()
        if not self.level_and_score:
            levelOne = Levels.objects.get(level_number=1)
            self.level_and_score, created = PlayerScore.objects.get_or_create(user=self.user, level=levelOne)
            self.level_and_score.save()

        self.level = str(self.level_and_score.level)
        self.score = self.level_and_score.current_level_score
        self.total_score = self.level_and_score.score

    def check_level_up(self):
        self.level_threshold = Levels.objects.filter(level_number=self.level).first()
        self.level_points_threshold = self.level_threshold.points_threshold
        self.points_needed = int(self.level_points_threshold) - int(self.score)

        # Update user level if score is more than current level threshold
        if self.score >= self.level_points_threshold:
            self.level = str(int(self.level) + 1)
            level_up = Levels.objects.filter(level_number=str(self.level)).first()
            self.level_and_score.level = level_up
            self.level_and_score.save()
            self.level_points_threshold = level_up.points_threshold

    def reset_status_data(self,request):
        self.initialized, created = PlayerStatus.objects.get_or_create(user=self.user)
        self.initialized.currentQuestion = 0
        self.initialized.currentScore = 0
        self.initialized.currentErrors = 0
        self.initialized.save()

        request.session['level_up'] = False


    def get(self, request):
        self.user = self.request.user

        self.reset_status_data(request)

        self.create_player_score_data()


        self.check_level_up()

        # Need to create answered data if doesn't exist
        #List of all user levels
        levels = list(range(1, int(self.level_and_score.level.level_number)+1))

        spanish_list_to_add = list()
        answered_data = Answered.objects.filter(user=self.user, level_int__in = levels)
        spanish_data = Spanish.objects.filter(level_number__in= levels)

        if len(answered_data) != len(spanish_data):
            for item in spanish_data:
                result = Answered.objects.filter(user = self.user,
                                                 spanish_id = item).count()

                if result == 0:
                    spanish_list_to_add.append(item)
        print('NEED to make', spanish_list_to_add)

        self.create_answered_data(spanish_list_to_add)

        self.find_streak_length()

        self.topic_strength = self.strength(str(self.level_and_score.level))

        context = {
            'user': self.user,
            'level': str(self.level_and_score.level),
            'total_score': self.total_score,
            'level_threshold': self.level_points_threshold,
            'points': self.points_needed,
            'strength': self.topic_strength,
            'level_description': self.level_threshold.description,
            'first_time': self.first_time,
        }

        return render(request, self.template_name, context)

    def save_current_level(self, level, user):
        current, created = PlayerStatus.objects.get_or_create(user=user)
        self.level_and_score = PlayerScore.objects.filter(user=user).first()

        current.current_level = level
        current.save()



    def post(self, request):
        if 'level_1.x' in request.POST:
            self.save_current_level(1, self.request.user)
            if self.level_and_score.level.level_number < 1:
                return redirect('/')
            return redirect('courses/level_info/')
        if 'level_2.x' in request.POST:
            self.save_current_level(2, self.request.user)
            if self.level_and_score.level.level_number < 2:
                return redirect('/')
            return redirect('courses/level_info/')
        if 'level_3.x' in request.POST:
            self.save_current_level(3, self.request.user)
            if self.level_and_score.level.level_number < 3:
                return redirect('/')
            return redirect('courses/level_info/')
        if 'level_4.x' in request.POST:
            self.save_current_level(4, self.request.user)
            if self.level_and_score.level.level_number < 4:
                return redirect('/')
            return redirect('courses/level_info/')
        if 'level_5.x' in request.POST:
            self.save_current_level(5, self.request.user)
            if self.level_and_score.level.level_number < 5:
                return redirect('/')
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

class UserActivity(LoginRequiredMixin, View):
    template_name = 'profile.html'

    def streak(self, session_object, streak_length):
        date = session_object.session
        yesterday = date - timedelta(days=1)
        result = UserSessions.objects.filter(user=self.user,
                                             session=str(yesterday)).first()
        print(result)
        if not result:
            return streak_length
        else:
            streak_length += 1
            return self.streak(result, streak_length)

    def get(self, request, **kwargs):
        all_sessions = UserSessions.objects.filter(user=self.request.user)
        session_arr = []

        self.user = self.request.user


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
        streak_length = 0
        if latest_session:
            streak_length = 1
            current_streak = self.streak(latest_session, streak_length)

        else:
            current_streak = 0

        longest_streak = PlayerScore.objects.filter(user=self.request.user).values('day_streak')[0]

        context = {
            'course_list': PlayerScore.objects.filter(user=self.request.user),
            'user': self.request.user,
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

    template_name = 'level_info.html'
    login_url = 'login'

    def reset_status_data(self):
    # If session level hasn't been given a value this means the session hasn't been initialized
        # For example if user has gone straightt to level info url without selecting a level previously
        self.initialized, created = PlayerStatus.objects.get_or_create(user=self.user)
        self.initialized.currentQuestion = 0
        self.initialized.currentScore = 0
        self.initialized.currentErrors = 0
        self.initialized.save()


    def get_quiz_data(self, request):

        if self.initialized.current_level != 0:
            current_level = [int(self.initialized.current_level),]
            answered_data = self.load_data(current_level, self.user)
            questions = self.get_questions2(answered_data, request)

        if self.initialized.current_level == 0:
            level = [self.initializeQuiz(request),]
            answered_data = self.load_data(level, self.user)
            self.get_questions2(answered_data, request)

    def check_if_user_quit_game_early(self, request):
        # if results is not empty it means that user has already started playing round and questions need to be reset to empty
        result = request.session['results']
        if len(result) != 0:
            # results is not empty - reset
            results = dict()
            request.session['results'] = results
            level = [self.initialized.current_level, ]
            answered_data = self.load_data(level, self.user)
            self.get_questions2(answered_data, request)

    def get_display_level_information(self):
        self.level = PlayerStatus.objects.filter(user=self.user).first()
        self.current_level = int(self.level.current_level)

        self.spanish_list = Spanish.objects.select_related('level_number').filter(level_number = self.current_level)

        level_desc = Levels.objects.filter(level_number=self.current_level).first()
        self.level_desc = level_desc.description


    def get_spanish_review_times_and_information_index(self):
        # Get review time for each item
        # Count number of items with additional information also (i)
        self.i = 0
        self.ready_to_review = list()

        today = timezone.now()
        answeredstuff = Answered.objects.filter(spanish_id__level_number__level_number=self.current_level,
                                                user = self.user)

        for item in answeredstuff:
            spanish = self.spanish_list.filter(spanish_phrase=item.spanish_id).first()

            review = item.review_time

            due = review - today

            due = due.days

            ls = (item.spanish_id, due)
            self.ready_to_review.append(ls)

            if str(spanish.information) != '':
                self.i = self.i + 1



    def convert_level_data_to_dictionary(self):
        # convert queryset to dictionary

        table_words = [{'spanish_phrase': obj.spanish_phrase,
                             'english_translation': obj.english_translation,
                             'information': obj.information} for obj in self.spanish_list]

        for item in table_words:
            for obj in self.ready_to_review:
                if str(item['spanish_phrase']) == str(obj[0]):
                    item['review_in'] = obj[1]
        return table_words

    def get(self, request):
        self.user = self.request.user

        self.reset_status_data()

        try:
            request.session['level_up']
        except:
            request.session['level_up'] = False

        self.get_quiz_data(request)

        self.check_if_user_quit_game_early(request)

        self.get_display_level_information()

        self.get_spanish_review_times_and_information_index()

        self.table_words = self.convert_level_data_to_dictionary()



        spanish_data = request.session['data']

        context = {
            'level': self.current_level,
            'level_now': self.level,
            'session_data': spanish_data,
            'description': self.level_desc,
            'NumWords': len(self.spanish_list),
            'level_up': request.session['level_up'],
            'ready_to_review': self.ready_to_review,
            'table_words': self.table_words,
            'NumInfo': self.i,
        }
        return render(request, self.template_name, context)

class ScoreBoard(LoginRequiredMixin,View):
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

class UserGuide(View):
    template_name = 'instructions.html'


    def get(self, request):

        context = {}

        return render(request, self.template_name, context)