# Generated by Django 2.2.5 on 2020-06-23 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='playerscore',
            name='day_streak',
            field=models.IntegerField(default=0),
        ),
    ]
