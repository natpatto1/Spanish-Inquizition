# Generated by Django 2.2.5 on 2020-08-25 21:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0010_playerstatus_review_game'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='playerstatus',
            name='review_game',
        ),
    ]
