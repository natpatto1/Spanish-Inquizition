# Generated by Django 2.2.5 on 2020-08-28 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0012_playerstatus_review_game'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='playerstatus',
            name='review_game',
        ),
        migrations.AddField(
            model_name='playerstatus',
            name='game',
            field=models.CharField(default='', max_length=100),
        ),
    ]
