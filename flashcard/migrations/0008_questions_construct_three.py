# Generated by Django 2.2.5 on 2020-08-11 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flashcard', '0007_remove_questions_construct_three'),
    ]

    operations = [
        migrations.AddField(
            model_name='questions',
            name='construct_three',
            field=models.CharField(default='', max_length=100),
        ),
    ]
