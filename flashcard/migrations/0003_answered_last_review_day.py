# Generated by Django 2.2.5 on 2020-07-03 14:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flashcard', '0002_auto_20200623_0942'),
    ]

    operations = [
        migrations.AddField(
            model_name='answered',
            name='last_review_day',
            field=models.DateField(default=datetime.date(2020, 7, 3)),
        ),
    ]
