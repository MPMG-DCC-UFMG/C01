# Generated by Django 3.2 on 2021-05-14 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20210512_1720'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='crawlrequest',
            name='crawler_type',
        ),
        migrations.AddField(
            model_name='crawlrequest',
            name='dynamic_processing',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
