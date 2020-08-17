# Generated by Django 2.2.5 on 2020-08-10 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('construct', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pronouns',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spanish', models.CharField(max_length=100)),
                ('person', models.CharField(choices=[('I', 'I'), ('you', 'you'), ('he', 'he'), ('she', 'she'), ('you, formal', 'you, formal'), ('we', 'we'), ('them all', 'them all'), ('they, masculine', 'they, masculine'), ('they, feminine', 'they, feminine'), ('them, formal', 'them, formal')], default='', max_length=100)),
                ('pronoun_type', models.CharField(choices=[('subjective', 'subjective'), ('possessive', 'possessive'), ('adjectives', 'adjectives'), ('prepositional', 'prepositional'), ('direct object', 'direct object '), ('reflexive', 'reflexive')], default='', max_length=100)),
            ],
        ),
    ]