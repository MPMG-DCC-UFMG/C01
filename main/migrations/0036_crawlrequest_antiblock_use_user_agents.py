# Generated by Django 3.0.3 on 2020-07-13 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0035_auto_20200713_1557'),
    ]

    operations = [
        migrations.AddField(
            model_name='crawlrequest',
            name='antiblock_use_user_agents',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
