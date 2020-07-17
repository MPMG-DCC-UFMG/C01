# Generated by Django 3.0.6 on 2020-05-21 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='crawlrequest',
            name='antiblock',
            field=models.CharField(choices=[(1, 'None'), (2, 'IP rotation'), (3, 'User-agent rotation'), (4, 'Random delays'), (5, 'Use proxy'), (6, 'Use cookies')], default='1', max_length=15),
        ),
    ]
