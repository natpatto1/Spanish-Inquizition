# Generated by Django 2.2.5 on 2020-08-11 12:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('flashcard', '0006_auto_20200810_2302'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='questions',
            name='construct_three',
        ),
    ]