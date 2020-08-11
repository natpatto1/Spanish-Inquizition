from django.db import models
from courses.models import Spanish, Levels
from django.forms import ModelForm
from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone
import datetime

#class ReviewPhrases(models.Model):
    #spanish = models.CharField(max_length=100,primary_key=True)
    #english = models.CharField(max_length=100)

    #def __str__(self):
        #return str(self.spanish)

#class Distractors(models.Model):
    #spanish = models.CharField(max_length=100)
    #distractor = models.models.ForeignKey(
        #Spanish,
        #on_delete=models.SET_NULL,

    #def __str__(self):
        #return (" for %s distract %s " %(str(self.spanish), str(self.distractor)))



class Questions(models.Model):
    level = models.PositiveIntegerField(default=1)
    spanish_id = models.ForeignKey(
        Spanish,
        on_delete=models.CASCADE,
    )
    correct_answer = models.CharField(max_length=100)
    distractor_one = models.CharField(max_length=100)
    distractor_two = models.CharField(max_length=100)
    distractor_three = models.CharField(max_length=100)
    distractor_four = models.CharField(max_length=100)
    construct_one = models.CharField(max_length=100, default='')
    construct_two = models.CharField(max_length=100, default='')
    construct_three = models.CharField(max_length=100, default='')

    def __str__(self):
        return str(self.spanish_id)


class Answered(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
    )
    spanish_id = models.ForeignKey(
        Spanish,
        on_delete=models.CASCADE,
    )
    quality_value = models.PositiveIntegerField(null=False, blank=False, default=0)
    repetition = models.PositiveIntegerField(null=False, blank=False, default=0)
    ef = models.FloatField(null=False, blank=False, default=2.5)
    review_time = models.DateTimeField(default= timezone.now)
    level_int = models.PositiveIntegerField(null=False, blank=False, default=1)
    last_review_day = models.DateField(default= timezone.now)


    def __str__(self):
        return (" level %s - %s " %(str(self.level_int), str(self.spanish_id)))


