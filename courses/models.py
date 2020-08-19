from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse




# Create your models here.
class Levels(models.Model):
    level_number_choices = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4,4),
        (5, 5),
    )
    level_number = models.PositiveIntegerField(null=False, blank=False,
                                               choices=level_number_choices, default=1, primary_key=True)
    points_threshold =models.PositiveIntegerField(null=False, blank=False)
    description = models.CharField(max_length= 400)

    def __str__(self):
        return str(self.level_number)

    def get_absolute_url(self):
        return reverse('level_detail', kwargs= self.level_number)



class Spanish(models.Model):
    spanish_phrase = models.CharField(max_length=100, primary_key=True)
    english_translation = models.CharField(max_length=100)
    previous = models.FloatField(null=False,blank=False,default=1.0)
    level_number = models.ForeignKey(
        Levels,
        on_delete=models.CASCADE,
    )
    information = models.CharField(max_length=1000, blank=True)
    type_choices = (
        ('verb', 'verb'),
        ('noun', 'noun'),
        ('pronoun', 'pronoun'),
        ('adjective/adverb', 'adjective/adverb'),
        ('question', 'question'),
        ('phrase','phrase'),
        ('greeting','greeting'),
        ('article','article'),
        ('preposition','preposition'),
    )
    type = models.CharField(max_length=200, null=False, choices=type_choices, default='')
    def __str__(self):
        return self.spanish_phrase


class PlayerScore(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete = models.CASCADE,
    )
    level = models.ForeignKey(
        Levels,
        on_delete=models.CASCADE,
    )
    score = models.IntegerField(default=0)
    day_streak = models.IntegerField(default=0)
    current_level_score = models.IntegerField(default=0)

    def __str__(self):
        return f"User-{self.user} | Level-{self.level} | Score {self.score}"

class PlayerStatus(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete= models.CASCADE,
    )
    current_level = models.IntegerField(default=0)
    currentQuestion = models.IntegerField(default=0)
    currentScore = models.IntegerField(default=0)
    currentErrors = models.IntegerField(default=0)

    def __str__(self):
        return f"Level-{self.current_level} | Question-{self.currentQuestion} | Score {self.currentScore}"


class UserSessions(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete= models.CASCADE,)
    session = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} | {self.session}"