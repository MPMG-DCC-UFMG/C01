# Generated by Django 3.0.8 on 2020-08-20 23:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0035_auto_20200820_2248'),
    ]

    operations = [
        migrations.AddField(
            model_name='crawlrequest',
            name='output_path',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]