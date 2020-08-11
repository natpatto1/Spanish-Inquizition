from django.db import models

# Create your models here.

class Verbs(models.Model):
    infinitive = models.CharField(max_length=100, primary_key=True)
    yo = models.CharField(max_length=100)
    tú = models.CharField(max_length=100)
    usted_él_ella = models.CharField(max_length=100)
    nosotros_nosotras = models.CharField(max_length=100)
    vosotros_vosotras = models.CharField(max_length=100)
    ustedes_ellos_ellas = models.CharField(max_length=100)

    def __str__(self):
        return self.infinitive

class Pronouns(models.Model):
    spanish = models.CharField(max_length=100)
    person_choices = (
        ('I', 'I'),
        ('you', 'you'),
        ('he', 'he'),
        ('she', 'she'),
        ('you, formal', 'you, formal'),
        ('we', 'we'),
        ('you all', 'you all'),
        ('they', 'they'),
        ('them, formal', 'them, formal'),
        ('he/she/you','he/she/you')
    )
    person = models.CharField(max_length=100, null=False, choices=person_choices, default='')
    pronoun_type_choices = (
        ('subjective', 'subjective'),
        ('possessive', 'possessive'),
        ('adjectives', 'adjectives'),
        ('prepositional','prepositional'),
        ('direct object', 'direct object '),
        ('reflexive','reflexive'),
    )
    pronoun_type = models.CharField(max_length=100, null=False, choices=pronoun_type_choices, default='')

    def __str__(self):
        return self.spanish

class Article(models.Model):
    spanish = models.CharField(max_length=100, primary_key=True)
    english = models.CharField(max_length=100)

    def __str__(self):
        return self.spanish