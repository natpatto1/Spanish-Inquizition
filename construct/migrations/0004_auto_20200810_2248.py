# Generated by Django 2.2.5 on 2020-08-10 22:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('construct', '0003_auto_20200810_2245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pronouns',
            name='person',
            field=models.CharField(choices=[('I', 'I'), ('you', 'you'), ('he', 'he'), ('she', 'she'), ('you, formal', 'you, formal'), ('we', 'we'), ('you all', 'you all'), ('they', 'they'), ('them, formal', 'them, formal'), ('he/she/you', 'he/she/you')], default='', max_length=100),
        ),
    ]