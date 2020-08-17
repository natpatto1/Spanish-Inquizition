# Generated by Django 2.2.5 on 2020-08-09 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0006_spanish_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spanish',
            name='type',
            field=models.CharField(choices=[('verb', 'verb'), ('noun', 'noun'), ('pronoun', 'pronoun'), ('adjective/adverb', 'adjective/adverb'), ('question', 'question'), ('phrase', 'phrase'), ('greeting', 'greeting')], default='', max_length=200),
        ),
    ]