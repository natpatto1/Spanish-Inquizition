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


