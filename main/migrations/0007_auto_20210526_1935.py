# Generated by Django 3.2 on 2021-05-26 19:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20210525_1655'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='crawlrequest',
            name='save_csv',
        ),
        migrations.RemoveField(
            model_name='crawlrequest',
            name='table_attrs',
        ),
    ]
